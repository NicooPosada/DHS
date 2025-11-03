from antlr4 import TerminalNode
from antlr4 import ErrorNode
from compiladorParser import compiladorParser
from compiladorListener import compiladorListener
from tabla_simbolos import TS, ID
class Escucha (compiladorListener) :
    indent = 1
    declaracion = 0
    profundidad = 0
    numNodos = 0

    def __init__(self):
        super().__init__()
        self.ts = TS.getTablaSimbolo()

    def enterPrograma(self, ctx:compiladorParser.ProgramaContext):
        print("Comienza el parsing")

    def exitPrograma(self, ctx:compiladorParser.ProgramaContext):
        print("Fin del parsing")
        print("\n" + "="*60)
        print("REPORTE DE LA TABLA DE SÍMBOLOS")
        print("="*60)
        print(self.ts)
        print("="*60)
        print("\n" + self.__str__())

    def enterIwhile(self, ctx:compiladorParser.IwhileContext):
        print("  "*self.indent + "Comienza while")
        self.indent += 1

    def exitIwhile(self, ctx:compiladorParser.IwhileContext):
        self.indent -= 1
        print("  "*self.indent + "Fin while")
    
    def enterBloque(self, ctx:compiladorParser.BloqueContext):
        print("  "*self.indent + "Comienza bloque - Creando nuevo contexto")
        self.ts.addContexto(f"bloque_{self.indent}")
        self.indent += 1
    
    def exitBloque(self, ctx:compiladorParser.BloqueContext):
        self.indent -= 1
        print("  "*self.indent + "Fin bloque - Eliminando contexto")
        ctx_eliminado = self.ts.delContexto()
        if ctx_eliminado:
            # Verificar variables no usadas en este contexto
            for nombre, simbolo in ctx_eliminado.simbolos.items():
                if not simbolo.usado:
                    print(f"  [WARNING] Variable '{nombre}' declarada pero no usada en {ctx_eliminado.nombre}")
    
    def enterIif(self, ctx:compiladorParser.IifContext):
        print("  "*self.indent + "Comienza if")
        self.indent += 1
    
    def exitIif(self, ctx:compiladorParser.IifContext):
        self.indent -= 1
        print("  "*self.indent + "Fin if")
    
    def enterIfor(self, ctx:compiladorParser.IforContext):
        print("  "*self.indent + "Comienza for")
        self.ts.addContexto(f"for_{self.indent}")
        self.indent += 1
    
    def exitIfor(self, ctx:compiladorParser.IforContext):
        self.indent -= 1
        print("  "*self.indent + "Fin for")
        self.ts.delContexto()

    def enterDeclaracion(self, ctx:compiladorParser.DeclaracionContext):
        self.declaracion += 1
    
    def exitDeclaracion(self, ctx:compiladorParser.DeclaracionContext):
        # Obtener el tipo
        tipo = ctx.tipo().getText() if ctx.tipo() else None
        
        # Obtener la lista de declaradores
        lista_declaradores = ctx.listaDeclaradores()
        if lista_declaradores is None:
            return
            
        # Extraer los nombres de las variables declaradas
        names = []
        inicializados = {}  # diccionario para saber cuáles están inicializados
        
        # Obtener todos los declaradores
        decls = lista_declaradores.declarador()
        if not isinstance(decls, list):
            decls = [decls]
        
        for d in decls:
            # Obtener el ID (nombre de la variable)
            id_token = d.ID() if hasattr(d, 'ID') else None
            if id_token:
                name = id_token.getText()
                names.append(name)
                
                # Verificar si tiene inicialización (ASIG presente)
                # d tiene la forma: ID | ID ASIG opal | ID CA NUMERO CC | ID CA NUMERO CC ASIG LLA listaOpal LLC
                tiene_asig = any(child.getText() == '=' for child in d.getChildren()) if hasattr(d, 'getChildren') else False
                inicializados[name] = tiene_asig
        
        # Registrar cada nombre en la tabla de símbolos
        for n in names:
            # Buscar solo en el contexto actual (no en contextos padres)
            simbolo_existente = self.ts.contextoActual().buscarSimboloLocal(n)
            if simbolo_existente:
                print(f"[ERROR] Redeclaración de '{n}' en el mismo contexto.")
            else:
                idobj = ID(nombre=n, tipo=tipo, inicializado=inicializados.get(n, False), usado=False)
                self.ts.addSimbolo(idobj)
                print(f"[OK] Declarada variable '{n}' tipo={tipo}, inicializada={inicializados.get(n, False)}")
    
    def enterAsignacion(self, ctx:compiladorParser.AsignacionContext):
        # ctx puede ser: ID ASIG opal | INCREMENT ID | DECREMENT ID | ID INCREMENT | ID DECREMENT
        ids = ctx.ID()
        if ids:
            if isinstance(ids, list):
                var_name = ids[0].getText()
            else:
                var_name = ids.getText()
            
            # Buscar la variable en la tabla de símbolos
            simbolo = self.ts.buscarSimbolo(var_name)
            if simbolo:
                # Marcar como inicializada y usada
                simbolo.setInicializado(True)
                simbolo.setUsado(True)
                print(f"  [INFO] Asignación a variable '{var_name}'")
            else:
                print(f"  [ERROR] Variable '{var_name}' no declarada (en asignación)")
    
    def enterFactor(self, ctx:compiladorParser.FactorContext):
        # factor puede ser: PA exp PC | ID | ID CA opal CC | NUMERO | llamadaFuncion
        id_token = ctx.ID()
        if id_token:
            var_name = id_token.getText()
            simbolo = self.ts.buscarSimbolo(var_name)
            if simbolo:
                if not simbolo.inicializado:
                    print(f"  [WARNING] Variable '{var_name}' usada antes de ser inicializada")
                simbolo.setUsado(True)
                print(f"  [INFO] Uso de variable '{var_name}'")
            else:
                print(f"  [ERROR] Variable '{var_name}' no declarada (en expresión)")
    
    def enterListaAsignaciones(self, ctx:compiladorParser.ListaAsignacionesContext):
        self.profundidad += 1
        
    def exitListaAsignaciones(self, ctx:compiladorParser.ListaAsignacionesContext):
        print("  -- ListaVar(%d) Cant. hijos  = %d" % (self.profundidad, ctx.getChildCount()))
        self.profundidad -= 1
        if ctx.getChildCount() == 4 :
            print("      hoja ID --> |%s|" % ctx.getChild(1).getText())

    # def visitTerminal(self, node: TerminalNode):
    #     print(" ---> Token: " + node.getText())
        # self.numTokens += 1
    
    def visitErrorNode(self, node: ErrorNode):
        print(" ---> ERROR")
        
    def enterEveryRule(self, ctx):
        self.numNodos += 1
    
    def __str__(self):
        return "Se hicieron " + str(self.declaracion) + " declaraciones\n" + \
                "Se visitaron " + str(self.numNodos) + " nodos"