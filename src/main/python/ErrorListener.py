from antlr4.error.ErrorListener import ErrorListener

class MiErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errores = [] 
    
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # Crear un diccionario con la información del error
        error = {
            'tipo': 'SINTÁCTICO',
            'linea': line,
            'columna': column,
            'mensaje': msg,
            'simbolo': offendingSymbol.text if offendingSymbol else '<EOF>'
        }
        self.errores.append(error)
        
        print(f"\n ERROR SINTÁCTICO [Línea {line}:{column}]")
        print(f"   Token:'{error['simbolo']}'")
        print(f"   Descripción: {msg}")
    
    def tiene_errores(self):
        return len(self.errores) > 0
    
    def obtener_reporte(self):
        if not self.errores:
            return "No se encontraron errores sintácticos"
        
        reporte = f"\n{'='*60}\n"
        reporte += f"REPORTE DE ERRORES SINTÁCTICOS ({len(self.errores)} encontrados)\n"
        reporte += f"{'='*60}\n"
        
        for i, err in enumerate(self.errores, 1):
            reporte += f"\n{i}. [{err['tipo']}] Línea {err['linea']}, Columna {err['columna']}\n"
            reporte += f"   Token: '{err['simbolo']}'\n"
            reporte += f"   {err['mensaje']}\n"
        
        return reporte