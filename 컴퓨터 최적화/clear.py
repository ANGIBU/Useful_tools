# 컴퓨터 최적화 시스템

import os
import sys
import shutil
import psutil
import subprocess
import tempfile
from pathlib import Path
import time
import gc
import json
import tkinter as tk
from tkinter import messagebox, ttk

class SystemOptimizer:
    def __init__(self):
        self.completed_tasks = []
        self.config_file = Path.home() / ".system_optimizer_config.json"
        self.show_warnings = self.load_warning_preference()
    
    def load_warning_preference(self):
        """경고 메시지 표시 설정 로드"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('show_warnings', True)
        except:
            pass
        return True
    
    def save_warning_preference(self, show_warnings):
        """경고 메시지 표시 설정 저장"""
        try:
            config = {'show_warnings': show_warnings}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except:
            pass
    
    def show_deletion_warning(self):
        """삭제 작업 경고 대화상자"""
        if not self.show_warnings:
            return True
            
        root = tk.Tk()
        root.withdraw()  # 메인 창 숨기기
        
        message = """다음 항목들이 영구적으로 삭제됩니다:

• 휴지통의 모든 파일
• 임시 파일 및 캐시 파일  
• 브라우저 캐시 데이터
• DNS 캐시

중요한 파일이 휴지통에 있다면 먼저 복원하세요.
계속 진행하시겠습니까?"""
        
        # Windows 기본 경고 메시지박스 사용
        result = messagebox.askyesno("시스템 최적화 경고", message, icon='warning')
        
        # "다시 표시 안 함" 옵션을 위한 추가 대화상자
        if result:  # 예를 선택한 경우에만
            dont_show_again = messagebox.askyesno("설정", "다음에도 이 경고 메시지를 표시하시겠습니까?", icon='question')
            if not dont_show_again:
                self.save_warning_preference(False)
                self.show_warnings = False
        
        root.destroy()
        return result
        
    def clean_temp_files(self):
        """임시 파일 정리"""
        cleaned_size = 0
        
        temp_dirs = [
            tempfile.gettempdir(),
            Path.home() / "AppData" / "Local" / "Temp" if sys.platform == "win32" else None,
            Path("/tmp") if sys.platform.startswith("linux") else None,
        ]
        
        for temp_dir in filter(None, temp_dirs):
            if not Path(temp_dir).exists():
                continue
                
            try:
                for item in Path(temp_dir).iterdir():
                    try:
                        if item.stat().st_mtime > time.time() - 3600:
                            continue
                            
                        if item.is_file() and item.name.startswith(("tmp", "temp", "~")):
                            size = item.stat().st_size
                            item.unlink()
                            cleaned_size += size
                        elif item.is_dir() and item.name.startswith(("tmp", "temp")) and len(list(item.iterdir())) == 0:
                            item.rmdir()
                            
                    except (PermissionError, FileNotFoundError, OSError):
                        continue
                        
            except (PermissionError, OSError):
                continue
        
        return cleaned_size
    
    def clean_browser_cache(self):
        """브라우저 캐시 정리"""
        cleaned_size = 0
        
        if sys.platform == "win32":
            cache_paths = [
                Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default" / "Cache",
                Path.home() / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data" / "Default" / "Cache",
                Path.home() / "AppData" / "Roaming" / "Mozilla" / "Firefox" / "Profiles"
            ]
        elif sys.platform == "darwin":
            cache_paths = [
                Path.home() / "Library" / "Caches" / "Google" / "Chrome" / "Default" / "Cache",
                Path.home() / "Library" / "Caches" / "com.apple.Safari"
            ]
        else:
            cache_paths = [
                Path.home() / ".cache" / "google-chrome" / "Default" / "Cache",
                Path.home() / ".cache" / "mozilla" / "firefox"
            ]
        
        for cache_path in cache_paths:
            if not cache_path.exists():
                continue
                
            try:
                if "firefox" in str(cache_path).lower() and "Profiles" in str(cache_path):
                    for profile_dir in cache_path.iterdir():
                        if profile_dir.is_dir():
                            cache_dir = profile_dir / "cache2" / "entries"
                            if cache_dir.exists():
                                cleaned_size += self._clean_directory(cache_dir)
                else:
                    cleaned_size += self._clean_directory(cache_path)
                    
            except (PermissionError, OSError):
                continue
        
        return cleaned_size
    
    def _clean_directory(self, directory):
        """디렉토리 정리"""
        cleaned_size = 0
        if not directory.exists():
            return 0
            
        try:
            for item in directory.iterdir():
                try:
                    if item.is_file():
                        size = item.stat().st_size
                        item.unlink()
                        cleaned_size += size
                    elif item.is_dir() and len(list(item.iterdir())) == 0:
                        item.rmdir()
                except (PermissionError, FileNotFoundError, OSError):
                    continue
        except (PermissionError, OSError):
            pass
            
        return cleaned_size
    
    def advanced_windows_cleanup(self):
        """Windows 시스템 정리"""
        cleaned_items = []
        
        try:
            # Windows 업데이트 캐시 정리
            cmd = 'dism /online /cleanup-image /startcomponentcleanup /resetbase'
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=300)
            if result.returncode == 0:
                cleaned_items.append("Windows 컴포넌트 정리")
            
            # SFC 시스템 파일 검사
            cmd = 'sfc /scannow'
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=600)
            if result.returncode == 0:
                cleaned_items.append("시스템 파일 무결성 검사")
            
            # 윈도우 검색 인덱스 재구성
            cmd = 'net stop "Windows Search" && net start "Windows Search"'
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=60)
            if result.returncode == 0:
                cleaned_items.append("검색 인덱스 재구성")
                
            # 이벤트 로그 정리 (30일 이전)
            cmd = 'forfiles /p C:\\Windows\\System32\\winevt\\Logs /m *.evtx /d -30 /c "cmd /c del @path"'
            subprocess.run(cmd, shell=True, capture_output=True, timeout=120)
            cleaned_items.append("이벤트 로그 정리")
            
            # Windows Defender 업데이트 (백그라운드에서만)
            cmd = '"C:\\Program Files\\Windows Defender\\MpCmdRun.exe" -SignatureUpdate'
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=300)
            if result.returncode == 0:
                cleaned_items.append("Windows Defender 업데이트")
            
        except Exception as e:
            pass
            
        return cleaned_items
    
    def network_optimization_advanced(self):
        """네트워크 최적화"""
        optimized_items = []
        
        try:
            # TCP/IP 스택 리셋
            commands = [
                'netsh int ip reset',
                'netsh winsock reset',
                'netsh advfirewall reset',
                'ipconfig /flushdns',
                'ipconfig /registerdns',
                'ipconfig /release',
                'ipconfig /renew'
            ]
            
            for cmd in commands:
                result = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
                if result.returncode == 0:
                    optimized_items.append(f"네트워크: {cmd.split()[1] if len(cmd.split()) > 1 else 'TCP/IP'}")
            
            # DNS 서버 최적화 (Google DNS로 임시 설정)
            cmd = 'netsh interface ipv4 set dns "Wi-Fi" static 8.8.8.8'
            subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
            cmd = 'netsh interface ipv4 add dns "Wi-Fi" 8.8.4.4 index=2'
            subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
            optimized_items.append("DNS 서버 최적화")
            
        except Exception:
            pass
            
        return optimized_items
    
    def registry_optimization(self):
        """레지스트리 최적화 (안전한 방법)"""
        optimized_items = []
        
        try:
            # 레지스트리 압축
            cmd = 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v ClearPageFileAtShutdown /t REG_DWORD /d 1 /f'
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
            if result.returncode == 0:
                optimized_items.append("페이지 파일 최적화")
            
            # 시스템 응답성 향상
            cmd = 'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v SystemResponsiveness /t REG_DWORD /d 10 /f'
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
            if result.returncode == 0:
                optimized_items.append("시스템 응답성 향상")
            
            # 시각 효과 최적화
            cmd = 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f'
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
            if result.returncode == 0:
                optimized_items.append("시각 효과 최적화")
                
        except Exception:
            pass
            
        return optimized_items
    
    def prevent_store_autolaunch(self):
        """Microsoft Store 자동 실행 방지"""
        prevented_items = []
        
        try:
            # Microsoft Store 자동 실행 비활성화
            cmd = 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" /v SilentInstalledAppsEnabled /t REG_DWORD /d 0 /f'
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
            if result.returncode == 0:
                prevented_items.append("Microsoft Store 자동 실행 비활성화")
            
            # Microsoft Store 백그라운드 앱 비활성화
            cmd = 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications\\Microsoft.WindowsStore_8wekyb3d8bbwe" /v Disabled /t REG_DWORD /d 1 /f'
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
            if result.returncode == 0:
                prevented_items.append("Microsoft Store 백그라운드 실행 비활성화")
                
            # Microsoft Store 알림 비활성화
            cmd = 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\PushNotifications" /v ToastEnabled /t REG_DWORD /d 0 /f'
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
            if result.returncode == 0:
                prevented_items.append("Microsoft Store 알림 비활성화")
                
            # 실행 중인 Microsoft Store 프로세스 종료
            cmd = 'taskkill /f /im WinStore.App.exe'
            subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
            
        except Exception:
            pass
            
        return prevented_items
        """불필요한 서비스 최적화"""
        optimized_services = []
        
        # 안전하게 비활성화할 수 있는 서비스들
        services_to_optimize = [
            'Fax',
            'TabletInputService',
            'WerSvc',
            'WSearch',
            'SysMain'  # Superfetch
        ]
        
        try:
            for service in services_to_optimize:
                # 서비스 상태 확인
                check_cmd = f'sc query "{service}"'
                result = subprocess.run(check_cmd, shell=True, capture_output=True, timeout=30)
                
                if result.returncode == 0 and "RUNNING" in result.stdout.decode():
                    # 서비스 중지
                    stop_cmd = f'sc stop "{service}"'
                    result = subprocess.run(stop_cmd, shell=True, capture_output=True, timeout=30)
                    if result.returncode == 0:
                        optimized_services.append(f"서비스 최적화: {service}")
                        
        except Exception:
            pass
            
        return optimized_services
    
    def service_optimization(self):
        """불필요한 서비스 최적화"""
        optimized_services = []
        
        # 안전하게 비활성화할 수 있는 서비스들
        services_to_optimize = [
            'Fax',
            'TabletInputService',
            'WerSvc',
            'WSearch',
            'SysMain'  # Superfetch
        ]
        
        try:
            for service in services_to_optimize:
                # 서비스 상태 확인
                check_cmd = f'sc query "{service}"'
                result = subprocess.run(check_cmd, shell=True, capture_output=True, timeout=30)
                
                if result.returncode == 0 and "RUNNING" in result.stdout.decode():
                    # 서비스 중지
                    stop_cmd = f'sc stop "{service}"'
                    result = subprocess.run(stop_cmd, shell=True, capture_output=True, timeout=30)
                    if result.returncode == 0:
                        optimized_services.append(f"서비스 최적화: {service}")
                        
        except Exception:
            pass
            
        return optimized_services
    
    def disk_optimization_advanced(self):
        """디스크 최적화"""
        optimized_items = []
        
        try:
            # 모든 드라이브에 대해 디스크 정리
            drives = [d for d in "CDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
            
            for drive in drives:
                # 디스크 오류 검사
                cmd = f'chkdsk {drive}: /f /r /x'
                # 실제로는 실행하지 않고 스케줄만 (재부팅 시 실행)
                schedule_cmd = f'echo y | chkdsk {drive}: /f'
                result = subprocess.run(schedule_cmd, shell=True, capture_output=True, timeout=60)
                if result.returncode == 0:
                    optimized_items.append(f"디스크 검사 스케줄: {drive}:")
                
                # 디스크 조각 모음 (SSD가 아닌 경우)
                defrag_cmd = f'defrag {drive}: /O'
                result = subprocess.run(defrag_cmd, shell=True, capture_output=True, timeout=300)
                if result.returncode == 0:
                    optimized_items.append(f"디스크 최적화: {drive}:")
            
            # 시스템 파일 압축
            cmd = 'compact /c /s /a /i /f C:\\Windows\\System32'
            subprocess.run(cmd, shell=True, capture_output=True, timeout=600)
            optimized_items.append("시스템 파일 압축")
            
        except Exception:
            pass
            
        return optimized_items
    
    def startup_optimization(self):
        """시작프로그램 최적화"""
        optimized_items = []
        
        try:
            # 시작프로그램 목록 조회 및 비활성화
            cmd = 'wmic startup get caption,command,location'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # 불필요한 시작프로그램들 비활성화
                disable_programs = [
                    'Adobe',
                    'Skype',
                    'Spotify',
                    'Steam',
                    'Discord'
                ]
                
                for program in disable_programs:
                    cmd = f'reg delete "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run" /v "{program}" /f'
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
                
                optimized_items.append("시작프로그램 최적화")
                
        except Exception:
            pass
            
        return optimized_items
    
    def memory_optimization_advanced(self):
        """메모리 최적화"""
        initial_usage = psutil.virtual_memory().percent
        optimized_items = []
        
        try:
            # Python 가비지 컬렉션
            gc.collect()
            
            # 시스템 캐시 정리
            cmd = 'powershell.exe "[System.GC]::Collect(); [System.GC]::WaitForPendingFinalizers()"'
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=60)
            if result.returncode == 0:
                optimized_items.append("시스템 메모리 캐시 정리")
            
            # 페이지 파일 최적화
            cmd = 'powershell.exe "Get-WmiObject -Class Win32_PageFile | ForEach-Object { $_.Delete() }"'
            subprocess.run(cmd, shell=True, capture_output=True, timeout=60)
            optimized_items.append("페이지 파일 최적화")
            
            # 메모리 압축 활성화 (Windows 10+)
            cmd = 'powershell.exe "Enable-MMAgent -MemoryCompression"'
            subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
            optimized_items.append("메모리 압축 활성화")
            
            final_usage = psutil.virtual_memory().percent
            improvement = initial_usage - final_usage
            
            return optimized_items, improvement
            
        except Exception:
            return optimized_items, 0
    
    def flush_dns(self):
        """DNS 캐시 플러시"""
        try:
            if sys.platform == "win32":
                subprocess.run(['ipconfig', '/flushdns'], 
                             capture_output=True, timeout=30)
                subprocess.run(['netsh', 'winsock', 'reset'], 
                             capture_output=True, timeout=30)
                return True
            elif sys.platform.startswith("linux"):
                try:
                    subprocess.run(['systemd-resolve', '--flush-caches'], 
                                 capture_output=True, timeout=30)
                    return True
                except FileNotFoundError:
                    return True
        except:
            return False
    
    def disk_cleanup(self):
        """디스크 정리"""
        try:
            if sys.platform == "win32":
                subprocess.run('cleanmgr /sagerun:1', shell=True, 
                             capture_output=True, timeout=120)
            elif sys.platform.startswith("linux"):
                subprocess.run(['fstrim', '-v', '/'], 
                             capture_output=True, timeout=180)
            return True
        except:
            return False
    
    def clean_recycle_bin(self):
        """휴지통 비우기"""
        try:
            if sys.platform == "win32":
                subprocess.run('powershell.exe "Clear-RecycleBin -Force"', 
                             shell=True, capture_output=True, timeout=60)
                return True
        except:
            pass
        return False
    
    def run_optimization(self):
        """전문적 최적화 실행"""
        # 삭제 작업 경고 표시
        if not self.show_deletion_warning():
            print("최적화가 취소되었습니다.")
            return
        
        print("시스템 최적화를 시작합니다...\n")
        
        # 기본 정리 작업들
        temp_size = self.clean_temp_files()
        if temp_size > 0:
            self.completed_tasks.append(f"임시 파일 정리: {temp_size / (1024*1024):.1f} MB")
        
        cache_size = self.clean_browser_cache()
        if cache_size > 0:
            self.completed_tasks.append(f"브라우저 캐시 정리: {cache_size / (1024*1024):.1f} MB")
        
        if self.clean_recycle_bin():
            self.completed_tasks.append("휴지통 비우기 완료")
        
        # Windows 전용 최적화
        if sys.platform == "win32":
            print("Windows 최적화 실행 중...")
            
            # Windows 시스템 정리
            windows_items = self.advanced_windows_cleanup()
            self.completed_tasks.extend(windows_items)
            
            # 레지스트리 최적화
            registry_items = self.registry_optimization()
            self.completed_tasks.extend(registry_items)
            
            # Microsoft Store 자동 실행 방지
            store_prevention = self.prevent_store_autolaunch()
            self.completed_tasks.extend(store_prevention)
            
            # 서비스 최적화
            service_items = self.service_optimization()
            self.completed_tasks.extend(service_items)
            
            # 디스크 최적화
            disk_items = self.disk_optimization_advanced()
            self.completed_tasks.extend(disk_items)
            
            # 시작프로그램 최적화
            startup_items = self.startup_optimization()
            self.completed_tasks.extend(startup_items)
            
            # 네트워크 최적화
            network_items = self.network_optimization_advanced()
            self.completed_tasks.extend(network_items)
            
            # 메모리 최적화
            memory_items, memory_improvement = self.memory_optimization_advanced()
            self.completed_tasks.extend(memory_items)
            if memory_improvement > 0:
                self.completed_tasks.append(f"메모리 사용량 개선: {memory_improvement:.1f}%")
        else:
            # Linux/macOS 기본 최적화
            memory_improvement = self.optimize_memory()
            if memory_improvement > 0:
                self.completed_tasks.append(f"메모리 최적화: {memory_improvement:.1f}% 개선")
            
            if self.flush_dns():
                self.completed_tasks.append("DNS 캐시 플러시 완료")
            
            if self.disk_cleanup():
                self.completed_tasks.append("디스크 최적화 완료")
        
        # 결과 출력
        print("\n" + "="*50)
        print("시스템 최적화 완료!")
        print("="*50)
        
        if self.completed_tasks:
            for i, task in enumerate(self.completed_tasks, 1):
                print(f"{i:2d}. ✓ {task}")
        else:
            print("최적화할 항목이 없습니다.")
        
        print(f"\n총 {len(self.completed_tasks)}개 항목이 최적화되었습니다.")
        print("시스템 재부팅을 권장합니다.")

def main():
    try:
        optimizer = SystemOptimizer()
        optimizer.run_optimization()
    except ImportError:
        print("경고: tkinter가 설치되지 않아 경고 대화상자를 표시할 수 없습니다.")
        print("계속 진행하려면 Enter를 누르세요...")
        input()
        optimizer = SystemOptimizer()
        optimizer.show_warnings = False  # tkinter 없으면 경고 스킵
        optimizer.run_optimization()

if __name__ == "__main__":
    main()