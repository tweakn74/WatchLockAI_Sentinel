import sys
import winreg
from pathlib import Path
from typing import List, Dict

# Verify essential library availability
try:
    import win32evtlog
    import win32api
    import win32process
    import win32service
    import win32con
except ImportError:
    print(
        "Error: The 'pywin32' library is required. Please install it with 'pip install pywin32'.",
        file=sys.stderr,
    )
    sys.exit(1)


# A centralized class for managing and reporting forensic findings.
class ForensicReport:
    """Manages and reports forensic findings with clear, structured output."""

    def __init__(self) -> None:
        self.findings: Dict[str, List[str]] = {
            "files_found": [],
            "registry_keys_found": [],
            "event_logs_found": [],
            "processes_found": [],
            "services_found": [],
        }

    def add_finding(self, category: str, message: str) -> None:
        """Adds a new finding to the report."""
        if category in self.findings:
            self.findings[category].append(message)
        else:
            print(f"Warning: Invalid report category '{category}'.", file=sys.stderr)

    def display(self) -> None:
        """Prints the final, structured forensic report."""
        print("\n--- Forensic Report ---")
        for category, items in self.findings.items():
            header = category.replace("_", " ").title()
            if items:
                print(f"[PASS] Possible {header} Found:")
                for item in items:
                    print(f"  - {item}")
            else:
                print(f"[FAIL] No {header} Found.")
        print("\n--- Scan Complete ---")


# --- Core Forensic Functions ---


def scan_file_system(report: ForensicReport) -> None:
    """Scans common user directories for Mimikatz-related files."""
    print("[SEARCH] Performing file system scan for known Mimikatz artifacts...")
    target_extensions = {".dmp", ".kirbi"}
    # Common Mimikatz executable names
    suspicious_names = {"mimikatz", "kiwi", "sekurlsa"}

    # Expanded search paths
    common_paths = [
        Path.home(),
        Path.home().joinpath("AppData", "Local", "Temp"),
        Path("C:\\Windows\\Temp"),
    ]

    for path in common_paths:
        if not path.exists() or not path.is_dir():
            continue
        try:
            # Use a generator for memory-efficient iteration
            for file_path in path.rglob("*"):
                try:
                    # Check file extensions
                    if file_path.suffix.lower() in target_extensions:
                        report.add_finding("files_found", str(file_path))

                    # Check suspicious names in file names
                    name_lower = file_path.name.lower()
                    if any(
                        suspicious_name in name_lower
                        for suspicious_name in suspicious_names
                    ):
                        report.add_finding(
                            "files_found", f"Suspicious name: {file_path}"
                        )
                except Exception:
                    # Continue processing other files
                    pass
        except Exception as e:
            print(f"Error scanning path '{path}': {e}", file=sys.stderr)


def scan_registry(report: ForensicReport) -> None:
    """Scans the Windows Registry for Mimikatz persistence mechanisms."""
    print("[DOC] Checking Windows Registry for persistence mechanisms...")
    reg_paths = [
        # Run keys
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        # RunOnce keys
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
        ),
        (
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
        ),
    ]

    for hive, subkey in reg_paths:
        try:
            with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        name, data, _type = winreg.EnumValue(key, i)
                        # Check for keywords and common Mimikatz paths
                        data_str = str(data).lower()
                        if (
                            "mimikatz" in data_str
                            or "sekurlsa" in data_str
                            or ".ps1" in data_str
                        ):
                            report.add_finding(
                                "registry_keys_found", f"{subkey}\\{name} -> {data}"
                            )
                        i += 1
                    except OSError:  # Stop iteration when no more values are found
                        break
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Error accessing registry path '{subkey}': {e}", file=sys.stderr)


def scan_event_logs(report: ForensicReport) -> None:
    """Scans PowerShell Event Logs for evidence of Mimikatz command execution."""
    print(
        "[U+23F3] Searching PowerShell event logs for historical activity (Event ID 4104)..."
    )
    log_names = ["Microsoft-Windows-PowerShell/Operational", "Security"]

    mimikatz_indicators = [
        "sekurlsa::",
        "Invoke-Mimikatz",
        "mimikatz.exe",
        "lsadump::",
        "kerberos::",
        "privilege::debug",
    ]

    event_ids = {
        "Microsoft-Windows-PowerShell/Operational": [4104],
        "Security": [4662, 4670, 4674],
    }

    for log_name in log_names:
        try:
            handle = win32evtlog.OpenEventLog(None, log_name)
            flags = (
                win32evtlog.EVENTLOG_BACKWARDS_READ
                | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            )
            total_read = 0

            while True:
                raw_events = win32evtlog.ReadEventLog(handle, flags, 0)
                if not raw_events:
                    break

                for event in raw_events:
                    # Check if this is an event we're interested in
                    if event.EventID in event_ids.get(log_name, []):
                        # Check for Mimikatz indicators in event data
                        try:
                            # For PowerShell script block logs
                            if hasattr(event, "StringInserts") and event.StringInserts:
                                for insert in event.StringInserts:
                                    if any(
                                        indicator in insert
                                        for indicator in mimikatz_indicators
                                    ):
                                        report.add_finding(
                                            "event_logs_found",
                                            f"{log_name} Event ID {event.EventID}: '{insert[:100]}...'",
                                        )
                        except Exception:
                            pass  # Continue processing other events

                total_read += len(raw_events)
                # Limit to avoid excessive runtime
                if total_read > 5000:
                    break

        except Exception:
            # Some logs might require elevated privileges
            pass
        finally:
            try:
                win32evtlog.CloseEventLog(handle)
            except Exception:
                pass


def scan_processes(report: ForensicReport) -> None:
    """Scans running processes for suspicious activity."""
    print("[RELOAD] Checking running processes for suspicious activity...")
    try:
        # Get list of running processes
        processes = win32process.EnumProcesses()

        suspicious_names = ["mimikatz", "lsass"]

        for pid in processes:
            try:
                # Open process to get name
                handle = win32api.OpenProcess(
                    win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                    False,
                    pid,
                )
                # Get the process name
                name = win32process.GetModuleBaseName(handle, 0)
                win32api.CloseHandle(handle)

                # Check for suspicious names
                name_lower = name.lower()
                if any(suspicious in name_lower for suspicious in suspicious_names):
                    report.add_finding("processes_found", f"PID {pid}: {name}")

            except Exception:
                # Process might have exited or we don't have permissions
                pass

    except Exception as e:
        print(f"Error scanning processes: {e}", file=sys.stderr)


def scan_services(report: ForensicReport) -> None:
    """Scans Windows services for suspicious entries."""
    print("[U+2699]  Checking Windows services for suspicious entries...")
    try:
        # Get handle to service control manager
        scm = win32service.OpenSCManager(
            None, None, win32service.SC_MANAGER_ENUMERATE_SERVICE
        )
        try:
            # Enumerate services
            services = win32service.EnumServicesStatus(scm)

            suspicious_names = ["mimikatz"]

            for service in services:
                name, display_name, status = service[:3]
                # Check for suspicious service names
                name_lower = name.lower()
                display_name_lower = display_name.lower()
                if any(
                    suspicious in name_lower for suspicious in suspicious_names
                ) or any(
                    suspicious in display_name_lower for suspicious in suspicious_names
                ):
                    report.add_finding(
                        "services_found",
                        f"Service: {name} ({display_name}) - Status: {status}",
                    )
        finally:
            win32service.CloseServiceHandle(scm)

    except Exception as e:
        print(f"Error scanning services: {e}", file=sys.stderr)


# --- Main Execution Block ---


def main() -> None:
    """The main entry point for the forensic scanner."""
    if not sys.platform.startswith("win"):
        print("This script is designed for Windows.", file=sys.stderr)
        sys.exit(1)

    print("--- Starting Enhanced Beazley-Protocol Mimikatz Forensic Scan ---")
    print(
        "Note: Some detection methods may be limited by event log retention policies."
    )
    report = ForensicReport()

    scan_file_system(report)
    scan_registry(report)
    scan_event_logs(report)
    scan_processes(report)
    scan_services(report)

    report.display()


if __name__ == "__main__":
    main()
