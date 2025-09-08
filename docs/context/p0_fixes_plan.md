# Top 5 P0 Compatibility Fixes - Implementation Plan

**Selected Priority Fixes (Max 5)**:

## Fix 1: Platform Guards for Registry Monitor
**File**: `collectors/reg_monitor.py`  
**Issue**: Registry monitoring will fail on Linux CI - needs platform check  
**Impact**: CI/Linux compatibility, prevents runtime crashes  
**Implementation**: Add `sys.platform` or `platform.system()` guard around Windows registry imports

## Fix 2: Platform Guards for Service Operations  
**File**: `service/service_wrapper.py`  
**Issue**: Service install/uninstall operations not guarded for Windows-only functions  
**Impact**: Cross-platform deployment safety  
**Implementation**: Guard service installation functions with platform checks

## Fix 3: Break Circular Import (config/app_core)
**File**: `app_core/config.py:109`  
**Issue**: `app_core.config` imports `config.operational_mode` creating potential cycle  
**Impact**: Reliable initialization, prevents import deadlocks  
**Implementation**: Use lazy import or move the import into the property method

## Fix 4: Platform Guards in Process Actions
**File**: `response/actions.py`  
**Issue**: Process termination may use Windows-specific operations without guards  
**Impact**: Process management safety across platforms  
**Implementation**: Add platform guards for Windows-specific process operations

## Fix 5: Standardize API Response Models
**File**: `console/web_api.py`  
**Issue**: Mix of Pydantic models and raw dicts in API responses creates inconsistency  
**Impact**: API contract consistency, type safety  
**Implementation**: Convert raw dict responses to proper Pydantic models

**Risk Assessment**: All fixes are low-risk, additive changes that improve robustness without breaking existing functionality.
