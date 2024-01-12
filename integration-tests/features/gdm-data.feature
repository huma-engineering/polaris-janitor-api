Feature: we can populate GDM patient data

  @fixture.mock.apis
  Scenario Outline: Populate a new day of data for GDM
    When the database has been reset with <gdm_patients> GDM, <dbm_patients> DBM, and <send_patients> SEND patients
    Then the running task completes within <reset_task_completes_in_seconds> seconds
    When we populate GDM data
    Then the running task completes within <gdm_populate_task_completes_in_seconds> seconds
    And patients with static uuids also have static MRNs

    Examples:
      | gdm_patients | dbm_patients | send_patients | reset_task_completes_in_seconds | gdm_populate_task_completes_in_seconds |
      | 2            | 2            | 2             | 240                             | 240                                     |
