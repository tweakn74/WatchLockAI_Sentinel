# Taint Flow Analysis Report v4.0

**Generated:** 2025-09-07  
**Scanner:** Credits Overdrive v4.0 Taint Flow Scanner  
**Repository:** WatchLockAI Sentinel

## Executive Summary

| Metric | Count | Details |
|--------|-------|---------|
| **Taint Sources** | 37 | Entry points for untrusted data |
| **Taint Sinks** | 46 | Potentially dangerous operations |
| **Data Flows** | 1105 | Source→sink paths identified |
| **Critical Flows** | 918 | Immediate security risks |
| **High Risk Flows** | 8 | Significant security concerns |
| **Mitigation Coverage** | 19.5% | Flows with detected mitigations |

## Risk Distribution

```
Critical: 918 flows - Immediate action required
High:       8 flows - Priority remediation  
Medium:    39 flows - Schedule for review
Low:      140 flows - Monitor
```

## Critical Findings

### 🚨 Critical Risk Flows

**1. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**2. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**3. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**4. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**5. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**6. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**7. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**8. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**9. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**10. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**11. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**12. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**13. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**14. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**15. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**16. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**17. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**18. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**19. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**20. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**21. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**22. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**23. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**24. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**25. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**26. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.Popen

**27. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.Popen

**28. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**29. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**30. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**31. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**32. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**33. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**34. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**35. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**36. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**37. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**38. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**39. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**40. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**41. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**42. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**43. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**44. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**45. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**46. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**47. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**48. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**49. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**50. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**51. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**52. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**53. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

**54. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/app.py:238` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

**55. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**56. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**57. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**58. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**59. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**60. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**61. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**62. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**63. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**64. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**65. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**66. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**67. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**68. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**69. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**70. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**71. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**72. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**73. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**74. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**75. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**76. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**77. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**78. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**79. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**80. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.Popen

**81. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_rbac_abuse.py:548` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.Popen

**82. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**83. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**84. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**85. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**86. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**87. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**88. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**89. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**90. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**91. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**92. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**93. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**94. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**95. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**96. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**97. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**98. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**99. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**100. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**101. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**102. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**103. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**104. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**105. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**106. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**107. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.Popen

**108. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_golden_payloads.py:443` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.Popen

**109. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**110. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**111. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**112. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**113. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**114. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**115. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**116. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**117. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**118. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**119. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**120. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**121. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**122. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**123. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**124. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**125. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**126. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**127. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**128. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**129. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**130. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**131. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**132. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**133. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**134. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.Popen

**135. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_quarantine_traversal.py:641` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.Popen

**136. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**137. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**138. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**139. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**140. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**141. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**142. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**143. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**144. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**145. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**146. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**147. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**148. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**149. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**150. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**151. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**152. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**153. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**154. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**155. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**156. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**157. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**158. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**159. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**160. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**161. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.Popen

**162. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tests/test_fuzz_inputs.py:597` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.Popen

**163. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**164. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**165. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**166. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**167. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**168. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**169. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**170. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**171. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**172. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**173. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**174. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**175. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**176. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**177. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**178. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**179. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**180. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**181. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**182. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**183. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**184. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**185. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**186. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**187. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.run

**188. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.Popen

**189. user_input 'env_value' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_value → subprocess.Popen

**190. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**191. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**192. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**193. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**194. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**195. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**196. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**197. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**198. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**199. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**200. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**201. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**202. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**203. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**204. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**205. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**206. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**207. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**208. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**209. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**210. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**211. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**212. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**213. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**214. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**215. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.Popen

**216. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/config_schema.py:205` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.Popen

**217. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**218. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**219. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**220. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**221. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**222. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**223. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**224. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**225. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**226. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**227. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**228. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**229. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**230. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**231. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**232. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**233. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**234. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**235. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**236. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**237. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**238. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**239. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**240. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**241. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**242. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.Popen

**243. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.Popen

**244. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**245. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**246. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**247. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**248. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**249. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**250. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**251. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**252. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**253. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**254. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**255. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**256. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**257. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**258. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**259. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**260. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**261. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**262. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**263. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**264. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**265. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**266. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**267. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**268. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**269. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

**270. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/preflight_checks.py:590` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

**271. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**272. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**273. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**274. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**275. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**276. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**277. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**278. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**279. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**280. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**281. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**282. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**283. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**284. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**285. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**286. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**287. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**288. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**289. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**290. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**291. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**292. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**293. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**294. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**295. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**296. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.Popen

**297. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:18` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.Popen

**298. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**299. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**300. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**301. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**302. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**303. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**304. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**305. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**306. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**307. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**308. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**309. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**310. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**311. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**312. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**313. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**314. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**315. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**316. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**317. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**318. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**319. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**320. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**321. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**322. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**323. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.Popen

**324. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.Popen

**325. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**326. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**327. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**328. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**329. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**330. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**331. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**332. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**333. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**334. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**335. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**336. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**337. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**338. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**339. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**340. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**341. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**342. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**343. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**344. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**345. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**346. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**347. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**348. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**349. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**350. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.Popen

**351. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:19` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.Popen

**352. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**353. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**354. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**355. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**356. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**357. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**358. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**359. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**360. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**361. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**362. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**363. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**364. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**365. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**366. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**367. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**368. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**369. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**370. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**371. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**372. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**373. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**374. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**375. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**376. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.run

**377. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.Popen

**378. user_input 'unknown' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** unknown → subprocess.Popen

**379. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**380. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**381. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**382. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**383. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**384. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**385. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**386. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**387. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**388. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**389. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**390. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**391. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**392. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**393. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**394. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**395. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**396. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**397. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**398. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**399. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**400. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**401. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**402. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**403. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.run

**404. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.Popen

**405. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/auth.py:20` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ✅ Present
- **Path:** env_var → subprocess.Popen

**406. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**407. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**408. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**409. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**410. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**411. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**412. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**413. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**414. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**415. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**416. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**417. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**418. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**419. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**420. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**421. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**422. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**423. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**424. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**425. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**426. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**427. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**428. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**429. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**430. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.run

**431. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.Popen

**432. user_input 'env_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/console/telemetry_export.py:173` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** env_var → subprocess.Popen

**433. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**434. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**435. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**436. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**437. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**438. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**439. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**440. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**441. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**442. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**443. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**444. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**445. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**446. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**447. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**448. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**449. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**450. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**451. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**452. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**453. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**454. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**455. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**456. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**457. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**458. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.Popen

**459. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.Popen

**460. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**461. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**462. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**463. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**464. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**465. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**466. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**467. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**468. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**469. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**470. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**471. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**472. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**473. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**474. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**475. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**476. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**477. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**478. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**479. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**480. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**481. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**482. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**483. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**484. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**485. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

**486. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

**487. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**488. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**489. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**490. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**491. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**492. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**493. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**494. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**495. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**496. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**497. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**498. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**499. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**500. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**501. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**502. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**503. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**504. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**505. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**506. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**507. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**508. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**509. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**510. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**511. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**512. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.Popen

**513. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.Popen

**514. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**515. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**516. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**517. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**518. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**519. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**520. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**521. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**522. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**523. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**524. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**525. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**526. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**527. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**528. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**529. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**530. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**531. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**532. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**533. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**534. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**535. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**536. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**537. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**538. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**539. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

**540. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/self_check.py:459` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

**541. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**542. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**543. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**544. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**545. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**546. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**547. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**548. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**549. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**550. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**551. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**552. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**553. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**554. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**555. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**556. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**557. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**558. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**559. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**560. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**561. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**562. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**563. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**564. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**565. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**566. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.Popen

**567. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.Popen

**568. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**569. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**570. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**571. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**572. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**573. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**574. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**575. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**576. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**577. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**578. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**579. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**580. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**581. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**582. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**583. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**584. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**585. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**586. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**587. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**588. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**589. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**590. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**591. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**592. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**593. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

**594. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/scenario_replayer.py:261` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

**595. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**596. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**597. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**598. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**599. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**600. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**601. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**602. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**603. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**604. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**605. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**606. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**607. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**608. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**609. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**610. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**611. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**612. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**613. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**614. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**615. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**616. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**617. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**618. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**619. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**620. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.Popen

**621. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.Popen

**622. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**623. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**624. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**625. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**626. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**627. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**628. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**629. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**630. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**631. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**632. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**633. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**634. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**635. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**636. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**637. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**638. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**639. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**640. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**641. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**642. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**643. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**644. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**645. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**646. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**647. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

**648. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/api_contract_check.py:452` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

**649. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**650. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**651. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**652. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**653. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**654. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**655. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**656. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**657. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**658. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**659. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**660. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**661. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**662. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**663. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**664. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**665. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**666. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**667. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**668. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**669. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**670. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**671. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**672. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**673. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**674. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.Popen

**675. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.Popen

**676. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**677. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**678. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**679. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**680. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**681. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**682. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**683. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**684. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**685. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**686. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**687. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**688. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**689. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**690. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**691. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**692. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**693. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**694. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**695. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**696. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**697. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**698. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**699. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**700. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**701. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

**702. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/rotate_secrets.py:334` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

**703. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**704. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**705. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**706. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**707. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**708. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**709. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**710. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**711. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**712. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**713. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**714. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**715. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**716. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**717. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**718. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**719. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**720. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**721. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**722. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**723. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**724. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**725. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**726. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**727. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.run

**728. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.Popen

**729. user_input 'ap' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** ap → subprocess.Popen

**730. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**731. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**732. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**733. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**734. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**735. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**736. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**737. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**738. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**739. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**740. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**741. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**742. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**743. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**744. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**745. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**746. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**747. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**748. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**749. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**750. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**751. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**752. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**753. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**754. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**755. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

**756. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:91` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

**757. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**758. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**759. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**760. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**761. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**762. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**763. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**764. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**765. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**766. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**767. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**768. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**769. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**770. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**771. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**772. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**773. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**774. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**775. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**776. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**777. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**778. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**779. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**780. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**781. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**782. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.Popen

**783. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.Popen

**784. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**785. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**786. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**787. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**788. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**789. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**790. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**791. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**792. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**793. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**794. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**795. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**796. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**797. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**798. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**799. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**800. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**801. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**802. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**803. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**804. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**805. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**806. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**807. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**808. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**809. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

**810. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/sec_lint.py:813` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

**811. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**812. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**813. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**814. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**815. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**816. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**817. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**818. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**819. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**820. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**821. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**822. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**823. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**824. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**825. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**826. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**827. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**828. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**829. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**830. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**831. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**832. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**833. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**834. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**835. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**836. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.Popen

**837. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.Popen

**838. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**839. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**840. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**841. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**842. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**843. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**844. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**845. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**846. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**847. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**848. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**849. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**850. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**851. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**852. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**853. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**854. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**855. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**856. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**857. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**858. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**859. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**860. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**861. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**862. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**863. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

**864. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/microbench.py:695` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

**865. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**866. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**867. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**868. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**869. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**870. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**871. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**872. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**873. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**874. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**875. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**876. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**877. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**878. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**879. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**880. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**881. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**882. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**883. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**884. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**885. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**886. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**887. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**888. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**889. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.run

**890. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.Popen

**891. user_input 'parser' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** parser → subprocess.Popen

**892. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/windows_install_dryrun.py:215` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**893. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_security_posture.py:34` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**894. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/generate_ga_signoff.py:246` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**895. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/scripts/package_release.py:143` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**896. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:42` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**897. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:63` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**898. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:82` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**899. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:103` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**900. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:172` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**901. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_offline_installer.py:191` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**902. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:71` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**903. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:91` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**904. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:111` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**905. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:138` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**906. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:157` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**907. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:177` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**908. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:204` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**909. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:224` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**910. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:258` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**911. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tests/test_windows_service.py:278` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**912. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/ui/tray_app.py:294` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**913. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/console/quarantine.py:97` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**914. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/verify_minimax_claims.py:770` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**915. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:107` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**916. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/composite_health_check.py:115` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.run

**917. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/repair_and_validate.py:87` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

**918. user_input 'tainted_var' flows to subprocess operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/tools/config_migrate.py:299` (user_input)
- **Sink:** `/workspace/WatchLockAI_Sentinel/tools/compat_matrix.py:11` (subprocess)
- **Mitigation:** ❌ Missing
- **Path:** tainted_var → subprocess.Popen

### ⚠️ High Risk Flows

**1. user_input 'parser' flows to sql operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541`
- **Sink:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:489`
- **Mitigation:** ❌

**2. user_input 'parser' flows to sql operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541`
- **Sink:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:517`
- **Mitigation:** ❌

**3. user_input 'parser' flows to sql operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541`
- **Sink:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:521`
- **Mitigation:** ❌

**4. user_input 'parser' flows to sql operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541`
- **Sink:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:525`
- **Mitigation:** ❌

**5. user_input 'tainted_var' flows to sql operation**
- **Source:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:541`
- **Sink:** `/workspace/WatchLockAI_Sentinel/detection/knowledge/loader.py:489`
- **Mitigation:** ❌

## Source Analysis

### By Type
- **Network:** 3 sources
- **User Input:** 34 sources

## Sink Analysis

### By Type
- **File Write:** 13 sinks
- **Network:** 2 sinks
- **Sql:** 4 sinks
- **Subprocess:** 27 sinks

## Path Security Analysis

### Quarantine Compliance
- ✅ No file path flows detected

## Recommendations

### High Priority
1. **Sanitize all user inputs** before use in file operations or subprocess calls
2. **Implement path validation** to restrict file operations to quarantine directories
3. **Use parameterized queries** for all database operations
4. **Add input validation** at API boundaries

### Medium Priority
1. **Implement rate limiting** for file upload endpoints
2. **Add logging** for all taint source→sink flows
3. **Review token handling** in file operations
4. **Enhance error handling** to prevent information leakage

### Monitoring
- Set up alerts for new critical/high risk flows
- Regular re-scanning after code changes
- Track mitigation coverage improvements

---
*Generated by Credits Overdrive v4.0 - Taint Flow Scanner*  
*Use tools/taint_scan.py to regenerate this report*
