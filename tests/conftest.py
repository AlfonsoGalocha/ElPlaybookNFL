import os
import sys

# Proyecto de layout plano (sin setup.py/paquete instalado): asegura que la raiz
# del repo este en sys.path pase lo que pase desde donde se invoque pytest.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
