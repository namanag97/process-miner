# API Bugs Identified

Generated: 2026-01-05T17:52:12.184358

## Summary

- **Total Issues**: 110
- **Critical**: 14
- **Major**: 96
- **Minor**: 0

## CRITICAL (14)

1. **POST /api/v1/auth/refresh - Server Crash (500)**
   - Status Code: 500
   - Description: Internal Server Error
   - Impact: Complete endpoint failure, server-side crash
   - Business Impact: Authentication flow broken, users cannot log in

2. **POST /api/v1/analyses - Server Crash (500)**
   - Status Code: 500
   - Description: Internal Server Error
   - Impact: Complete endpoint failure, server-side crash
   - Business Impact: Process analysis features cannot be accessed

3. **GET /api/v1/visualization/{dataset_id}/explorer-data - Server Crash (500)**
   - Status Code: 500
   - Description: Internal Server Error
   - Impact: Complete endpoint failure, server-side crash

4. **GET /api/v1/ocpm/datasets/{dataset_id}/object-types - Server Crash (500)**
   - Status Code: 500
   - Description: Internal Server Error
   - Impact: Complete endpoint failure, server-side crash

5. **DELETE /api/v1/filtering/datasets/{dataset_id}/results/{filtered_id} - Server Crash (500)**
   - Status Code: 500
   - Description: Internal Server Error
   - Impact: Complete endpoint failure, server-side crash

6. **GET /api/v1/analytics/datasets/{dataset_id}/bottlenecks - Server Crash (500)**
   - Status Code: 500
   - Description: Internal Server Error
   - Impact: Complete endpoint failure, server-side crash

7. **GET /api/v1/analytics/datasets/{dataset_id}/rework - Server Crash (500)**
   - Status Code: 500
   - Description: Internal Server Error
   - Impact: Complete endpoint failure, server-side crash

8. **GET /api/v1/analytics/datasets/{dataset_id}/service-times - Server Crash (500)**
   - Status Code: 500
   - Description: Internal Server Error
   - Impact: Complete endpoint failure, server-side crash

9. **GET /api/v1/analytics/datasets/{dataset_id}/rework-chains - Server Crash (500)**
   - Status Code: 500
   - Description: Internal Server Error
   - Impact: Complete endpoint failure, server-side crash

10. **GET /api/v1/jobs/{job_id} - Server Crash (500)**
   - Status Code: 500
   - Description: Internal Server Error
   - Impact: Complete endpoint failure, server-side crash
   - Business Impact: Job monitoring and background task management unavailable

11. **DELETE /api/v1/jobs/{job_id} - Server Crash (500)**
   - Status Code: 500
   - Description: Internal Server Error
   - Impact: Complete endpoint failure, server-side crash
   - Business Impact: Job monitoring and background task management unavailable

12. **GET /api/v1/jobs/{job_id}/stream - Server Crash (500)**
   - Status Code: 500
   - Description: Internal Server Error
   - Impact: Complete endpoint failure, server-side crash
   - Business Impact: Job monitoring and background task management unavailable

13. **GET /api/v1/dev/data/tables - Server Crash (500)**
   - Status Code: 500
   - Description: Internal Server Error
   - Impact: Complete endpoint failure, server-side crash

14. **POST /api/v1/telemetry/traces - Server Crash (500)**
   - Status Code: 500
   - Description: Internal Server Error
   - Impact: Complete endpoint failure, server-side crash

## MAJOR (96)

1. **POST /api/v1/auth/register - Client Error on Valid Request (400)**
   - Status Code: 400
   - Description: Bad Request
   - Impact: Valid request rejected by server, possible validation issue
   - Business Impact: Authentication flow broken, users cannot log in

2. **POST /api/v1/auth/login - Client Error on Valid Request (401)**
   - Status Code: 401
   - Description: Unauthorized
   - Impact: Valid request rejected by server, possible validation issue
   - Business Impact: Authentication flow broken, users cannot log in

3. **GET /api/v1/workspaces/{workspace_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist
   - Business Impact: Workspace management functionality broken

4. **PUT /api/v1/workspaces/{workspace_id} - Client Error on Valid Request (422)**
   - Status Code: 422
   - Description: Unprocessable Content
   - Impact: Valid request rejected by server, possible validation issue
   - Business Impact: Workspace management functionality broken

5. **DELETE /api/v1/workspaces/{workspace_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist
   - Business Impact: Workspace management functionality broken

6. **POST /api/v1/workspaces/{workspace_id}/projects/{project_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist
   - Business Impact: Workspace management functionality broken

7. **DELETE /api/v1/workspaces/{workspace_id}/projects/{project_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist
   - Business Impact: Workspace management functionality broken

8. **POST /api/v1/projects - Client Error on Valid Request (400)**
   - Status Code: 400
   - Description: Bad Request
   - Impact: Valid request rejected by server, possible validation issue
   - Business Impact: Project operations unavailable

9. **GET /api/v1/projects/{project_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist
   - Business Impact: Project operations unavailable

10. **PUT /api/v1/projects/{project_id} - Client Error on Valid Request (422)**
   - Status Code: 422
   - Description: Unprocessable Content
   - Impact: Valid request rejected by server, possible validation issue
   - Business Impact: Project operations unavailable

11. **DELETE /api/v1/projects/{project_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist
   - Business Impact: Project operations unavailable

12. **POST /api/v1/projects/{project_id}/files/{dataset_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist
   - Business Impact: Project operations unavailable

13. **DELETE /api/v1/projects/{project_id}/files/{dataset_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist
   - Business Impact: Project operations unavailable

14. **POST /api/v1/datasets/upload/presigned - Client Error on Valid Request (422)**
   - Status Code: 422
   - Description: Unprocessable Content
   - Impact: Valid request rejected by server, possible validation issue

15. **POST /api/v1/datasets/{dataset_id}/trigger-validation - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

16. **POST /api/v1/datasets/upload - Client Error on Valid Request (422)**
   - Status Code: 422
   - Description: Unprocessable Content
   - Impact: Valid request rejected by server, possible validation issue

17. **POST /api/v1/datasets/detect-columns - Client Error on Valid Request (422)**
   - Status Code: 422
   - Description: Unprocessable Content
   - Impact: Valid request rejected by server, possible validation issue

18. **POST /api/v1/datasets/{dataset_id}/ingest - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

19. **GET /api/v1/datasets/{dataset_id}/detect-columns - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

20. **GET /api/v1/datasets/{dataset_id}/preview - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

21. **GET /api/v1/datasets/{dataset_id}/sheets - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

22. **GET /api/v1/datasets/{dataset_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

23. **DELETE /api/v1/datasets/{dataset_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

24. **GET /api/v1/datasets/{dataset_id}/statistics - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

25. **GET /api/v1/datasets/{dataset_id}/cases - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

26. **GET /api/v1/datasets/{dataset_id}/variants - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

27. **GET /api/v1/datasets/{dataset_id}/activities - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

28. **GET /api/v1/datasets/{dataset_id}/domain/analysis - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

29. **GET /api/v1/analyses/{analysis_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist
   - Business Impact: Process analysis features cannot be accessed

30. **DELETE /api/v1/analyses/{analysis_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist
   - Business Impact: Process analysis features cannot be accessed

31. **GET /api/v1/analyses/log/{dataset_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist
   - Business Impact: Process analysis features cannot be accessed

32. **POST /api/v1/discovery/discover - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

33. **GET /api/v1/discovery/models/{model_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

34. **DELETE /api/v1/discovery/models/{model_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

35. **GET /api/v1/visualization/{dataset_id}/dfg - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

36. **GET /api/v1/visualization/models/{model_id}/petri - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

37. **GET /api/v1/visualization/models/{model_id}/svg - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

38. **GET /api/v1/visualization/{dataset_id}/dfg/svg - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

39. **GET /api/v1/visualization/{dataset_id}/footprints - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

40. **POST /api/v1/conformance/check - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

41. **GET /api/v1/conformance/results/{result_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

42. **DELETE /api/v1/conformance/results/{result_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

43. **GET /api/v1/conformance/diagnostics/{dataset_id}/{model_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

44. **GET /api/v1/conformance/deviations/{dataset_id}/{model_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

45. **GET /api/v1/conformance/alignments/{dataset_id}/{model_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

46. **GET /api/v1/conformance/quality/{dataset_id}/{model_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

47. **POST /api/v1/conformance/import-model - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

48. **GET /api/v1/conformance/root-cause/{dataset_id}/{model_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

49. **GET /api/v1/conformance/deviations/by-activity/{dataset_id}/{model_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

50. **GET /api/v1/conformance/deviations/by-position/{dataset_id}/{model_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

51. **GET /api/v1/conformance/deviations/attribute-correlation/{dataset_id}/{model_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

52. **GET /api/v1/business/p2p/mavericks/{dataset_id}/{reference_model_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

53. **GET /api/v1/business/p2p/audit-report/{dataset_id}/{reference_model_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

54. **GET /api/v1/business/o2c/split-log/{dataset_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

55. **GET /api/v1/business/o2c/compare/{dataset_id1}/{dataset_id2} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

56. **POST /api/v1/business/supply-chain/simulate/{dataset_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

57. **GET /api/v1/business/customer-journey/dropoffs/{dataset_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

58. **POST /api/v1/ocpm/upload - Client Error on Valid Request (422)**
   - Status Code: 422
   - Description: Unprocessable Content
   - Impact: Valid request rejected by server, possible validation issue

59. **GET /api/v1/ocpm/datasets/{dataset_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

60. **DELETE /api/v1/ocpm/datasets/{dataset_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

61. **GET /api/v1/ocpm/datasets/{dataset_id}/statistics - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

62. **POST /api/v1/ocpm/discover - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

63. **GET /api/v1/ocpm/models/{model_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

64. **DELETE /api/v1/ocpm/models/{model_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

65. **GET /api/v1/ocpm/datasets/{dataset_id}/relationships - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

66. **GET /api/v1/ocpm/datasets/{dataset_id}/oc-dfg - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

67. **POST /api/v1/ocpm/datasets/{dataset_id}/flatten - Client Error on Valid Request (422)**
   - Status Code: 422
   - Description: Unprocessable Content
   - Impact: Valid request rejected by server, possible validation issue

68. **POST /api/v1/workflows - Client Error on Valid Request (400)**
   - Status Code: 400
   - Description: Bad Request
   - Impact: Valid request rejected by server, possible validation issue

69. **GET /api/v1/workflows/{workflow_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

70. **DELETE /api/v1/workflows/{workflow_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

71. **POST /api/v1/workflows/{workflow_id}/run - Client Error on Valid Request (422)**
   - Status Code: 422
   - Description: Unprocessable Content
   - Impact: Valid request rejected by server, possible validation issue

72. **GET /api/v1/workflows/runs/{run_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

73. **POST /api/v1/filtering/datasets/{dataset_id}/apply - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

74. **POST /api/v1/filtering/datasets/{dataset_id}/preview - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

75. **GET /api/v1/filtering/datasets/{dataset_id}/options - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

76. **GET /api/v1/filtering/datasets/{dataset_id}/results - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

77. **GET /api/v1/analytics/datasets/{dataset_id}/cycle-time - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

78. **GET /api/v1/analytics/datasets/{dataset_id}/throughput - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

79. **GET /api/v1/analytics/datasets/{dataset_id}/patterns - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

80. **GET /api/v1/analytics/datasets/{dataset_id}/performance - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

81. **GET /api/v1/organizational/datasets/{dataset_id}/handover-network - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

82. **GET /api/v1/organizational/datasets/{dataset_id}/collaboration-network - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

83. **GET /api/v1/organizational/datasets/{dataset_id}/resource-similarity - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

84. **GET /api/v1/organizational/datasets/{dataset_id}/roles - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

85. **GET /api/v1/organizational/datasets/{dataset_id}/resources/{resource}/profile - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

86. **GET /api/v1/organizational/datasets/{dataset_id}/workload - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

87. **POST /api/v1/predictions/datasets/{dataset_id}/train - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

88. **GET /api/v1/predictions/predictors/{predictor_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

89. **DELETE /api/v1/predictions/predictors/{predictor_id} - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

90. **POST /api/v1/predictions/predictors/{predictor_id}/predict - Client Error on Valid Request (422)**
   - Status Code: 422
   - Description: Unprocessable Content
   - Impact: Valid request rejected by server, possible validation issue

91. **POST /api/v1/predictions/predictors/{predictor_id}/predict-batch - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

92. **POST /api/v1/simulation/models/{model_id}/play-out - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

93. **POST /api/v1/simulation/datasets/{dataset_id}/simulate - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

94. **POST /api/v1/simulation/datasets/{dataset_id}/capacity-plan - 404 Not Found**
   - Status Code: 404
   - Description: Endpoint or resource not found
   - Impact: Endpoint may not be implemented or resource doesn't exist

95. **GET /api/v1/dev/data/records/{table} - Client Error on Valid Request (400)**
   - Status Code: 400
   - Description: Bad Request
   - Impact: Valid request rejected by server, possible validation issue

96. **GET /api/v1/dev/data/record/{table}/{record_id} - Client Error on Valid Request (400)**
   - Status Code: 400
   - Description: Bad Request
   - Impact: Valid request rejected by server, possible validation issue

