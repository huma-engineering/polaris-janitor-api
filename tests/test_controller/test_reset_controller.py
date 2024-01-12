import datetime
import uuid
from functools import partial
from typing import Any, Dict

import httpx
import pytest
from flask import Flask
from flask_batteries_included.helpers.error_handler import ServiceUnavailableException
from pytest_mock import MockFixture
from respx import MockRouter

from dhos_janitor_api.blueprint_api import ClientRepository
from dhos_janitor_api.blueprint_api.controller import reset_controller

PRODUCT_SETTINGS: Dict[str, Dict[str, Any]] = {
    "GDM": {"number_of_patients": 20},
    "DBM": {"number_of_patients": 20},
    "SEND": {"number_of_patients": 20},
}


class TestResetController:
    @pytest.mark.parametrize(
        "reset_request",
        (
            {},
            {"targets": ["dhos-notareal-api"]},
            {"targets": ["dhos-services-api", "dhos-locations-api"]},
        ),
    )
    @pytest.mark.parametrize("status_code", (200, 404))
    @pytest.mark.parametrize("use_epr_integration", (True, False))
    def test_reset_microservices(
        self,
        app: Flask,
        clients: ClientRepository,
        respx_mock: MockRouter,
        mocker: MockFixture,
        reset_request: Dict,
        status_code: int,
        use_epr_integration: bool,
    ) -> None:
        targets = (
            reset_request["targets"]
            if reset_request
            else app.config["RESETTABLE_TARGETS"]
        )
        trustomer_config = {
            "uuid": str(uuid.uuid4()),
            "created": datetime.datetime.utcnow().astimezone().isoformat(),
            "gdm_config": {"use_epr_integration": use_epr_integration},
        }
        mock_populate_service = mocker.patch.object(
            reset_controller, "populate_service"
        )
        mock_drop = respx_mock.post("/gdm/v2/internal/drop_data").mock(
            return_value=httpx.Response(status_code=status_code, json={})
        )
        mock_trustomer_config = mocker.patch.object(
            reset_controller.trustomer_client,
            "get_trustomer_config",
            return_value=trustomer_config,
        )

        reset = partial(
            reset_controller.reset_microservices,
            clients,
            reset_request,
            PRODUCT_SETTINGS,
        )

        if "dhos-notareal-api" in targets or (
            "dhos-fuego-api" in targets and not use_epr_integration
        ):
            with pytest.raises(ValueError):
                reset()
            assert not mock_drop.called
            mock_trustomer_config.assert_called_once()
            return

        if status_code == 404:
            with pytest.raises(ServiceUnavailableException):
                reset()
            assert mock_drop.called
            mock_trustomer_config.assert_called_once()
            return

        reset()
        assert mock_drop.called
        mock_trustomer_config.assert_called_once()
        mock_populate_service.assert_called()

    def test_make_location_hospital(self) -> None:
        hospital = reset_controller.make_location(reset_controller.HOSPITAL_SCT_CODE)
        assert "Hospital" in hospital["display_name"]
        assert hospital["location_type"] == reset_controller.HOSPITAL_SCT_CODE
        assert hospital.get("parent") is None

    def test_make_location_ward(self) -> None:
        hospital = reset_controller.make_location(reset_controller.HOSPITAL_SCT_CODE)
        ward = reset_controller.make_location(
            reset_controller.WARD_SCT_CODE, hospital, suffix="1"
        )
        assert "Ward" in ward["display_name"]
        assert ward["location_type"] == reset_controller.WARD_SCT_CODE
        assert ward["parent"] == hospital["uuid"]

    def test_make_location_bay(self) -> None:
        hospital = reset_controller.make_location(reset_controller.HOSPITAL_SCT_CODE)
        ward = reset_controller.make_location(
            reset_controller.WARD_SCT_CODE, hospital, suffix="1"
        )
        bay = reset_controller.make_location(
            reset_controller.BAY_SCT_CODE, ward, suffix="1"
        )
        assert "Bay" in bay["display_name"]
        assert bay["location_type"] == reset_controller.BAY_SCT_CODE
        assert bay["parent"] == ward["uuid"]

    def test_make_location_bed(self) -> None:
        hospital = reset_controller.make_location(reset_controller.HOSPITAL_SCT_CODE)
        ward = reset_controller.make_location(
            reset_controller.WARD_SCT_CODE, hospital, suffix="1"
        )
        ward2 = reset_controller.make_location(
            reset_controller.WARD_SCT_CODE, hospital, suffix="2"
        )
        bay = reset_controller.make_location(
            reset_controller.BAY_SCT_CODE, ward, suffix="1"
        )
        bed = reset_controller.make_location(
            reset_controller.BED_SCT_CODE, bay, suffix="1"
        )
        bed2 = reset_controller.make_location(
            reset_controller.BED_SCT_CODE, ward2, suffix="1"
        )

        assert "Bed" in bed["display_name"] and "Bed" in bed2["display_name"]
        assert bed["location_type"] == reset_controller.BED_SCT_CODE
        assert bed2["location_type"] == reset_controller.BED_SCT_CODE
        assert bed["parent"] == bay["uuid"]
        assert bed2["parent"] == ward2["uuid"]

    def test_ensure_mrn_is_static(
        self, app: Flask, clients: ClientRepository, mocker: MockFixture
    ) -> None:
        mocker.patch.object(
            reset_controller.trustomer_client,
            "get_trustomer_config",
            return_value={
                "uuid": str(uuid.uuid4()),
                "created": datetime.datetime.utcnow().astimezone().isoformat(),
                "gdm_config": {"medication_tags": "gdm-uk-default"},
                "dbm_config": {"medication_tags": "dbm-uk-default"},
            },
        )
        mocker.patch.object(
            reset_controller.generator_controller.users_client,
            "get_clinicians",
            return_value=[{}],
        )
        mocker.patch.object(
            reset_controller.generator_controller.medication_client,
            "get_medications",
            return_value=[{"sct_code": 123}],
        )
        gdm_patients = reset_controller._open_and_closed_patients(
            clients, PRODUCT_SETTINGS["GDM"]["number_of_patients"], "GDM"
        )
        dbm_patients = reset_controller._open_and_closed_patients(
            clients, PRODUCT_SETTINGS["DBM"]["number_of_patients"], "DBM"
        )

        for p in gdm_patients + dbm_patients:
            if p["uuid"].startswith("static"):
                i = p["uuid"].split("_")[-1]
                assert p["hospital_number"] == i * 6

    def test_start_reset_thread(self, mocker: MockFixture) -> None:
        class Cls:
            @staticmethod
            def start(
                reset_request: Dict, product_settings: Dict, location_config: Dict
            ) -> None:
                return None

        m = mocker.patch.object(
            reset_controller,
            "JanitorThread",
            return_value=Cls,
        )
        reset_controller.start_reset_thread({}, {}, 1, 1)

        assert m.call_count == 1

    def test_populate_service_bad(self, clients: ClientRepository) -> None:
        with pytest.raises(ValueError):
            reset_controller.populate_service(
                clients,
                "fake_service",
                {},
                {"hospitals": 1, "wards": 1},
            )

    def test_get_random_clinician_jwt_header(self, mocker: MockFixture) -> None:
        clinician = {"uuid": "UUID1", "email_address": "email@mail.com"}

        c = mocker.patch.object(
            reset_controller,
            "get_random_clinician",
            return_value=clinician,
        )
        mock_get_clinician_jwt = mocker.patch.object(
            reset_controller.auth_controller, "get_clinician_jwt", return_value=""
        )
        c_jwt = reset_controller.get_random_clinician_jwt(
            [clinician],
            {"GDM Superclinician"},
        )
        mock_get_clinician_jwt.assert_called_once()
        c.assert_called_once()
        assert c_jwt == ""
