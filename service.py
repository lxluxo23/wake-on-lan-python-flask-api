import win32serviceutil
import win32service
import win32event
import servicemanager
import logging
import os
import sys
import threading
from waitress import serve
from app import create_app

class WakeOnLanService(win32serviceutil.ServiceFramework):
    _svc_name_ = "WakeOnLanAPI"
    _svc_display_name_ = "Wake-on-LAN API Service"
    _svc_description_ = "Servicio para controlar equipos remotamente con Wake-on-LAN"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        self.setup_logging()

    def setup_logging(self):
        """Configurar logging para el servicio"""
        # Crear directorio de logs si no existe
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configurar logging
        log_file = os.path.join(log_dir, 'wake_service.log')
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # También log al Event Viewer de Windows
        self.logger = logging.getLogger('WakeOnLanService')
        
    def SvcStop(self):
        """Detener el servicio"""
        self.logger.info("Deteniendo servicio Wake-on-LAN...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        """Ejecutar el servicio"""
        try:
            self.logger.info("Iniciando servicio Wake-on-LAN...")
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
            
            # Crear la aplicación Flask
            app = create_app()
            
            # Ejecutar servidor en un thread separado
            def run_server():
                try:
                    self.logger.info("Servidor iniciando en puerto 90...")
                    serve(app, host='0.0.0.0', port=90)
                except Exception as e:
                    self.logger.error(f"Error en servidor: {e}")
                    
            server_thread = threading.Thread(target=run_server)
            server_thread.daemon = True
            server_thread.start()
            
            self.logger.info("Servicio Wake-on-LAN iniciado correctamente")
            
            # Esperar señal de parada
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            
        except Exception as e:
            self.logger.error(f"Error crítico en servicio: {e}")
            servicemanager.LogErrorMsg(f"Error en servicio Wake-on-LAN: {e}")
        finally:
            self.logger.info("Servicio Wake-on-LAN detenido")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(WakeOnLanService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(WakeOnLanService)