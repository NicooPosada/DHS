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




    #Inicializamos la tabla de simbolos
    def __init__(self):
        super().__init__()
        self.ts = TS.getTablaSimbolo()

    def enterPrograma(self, ctx:compiladorParser.ProgramaContext):
        print("Comienza el parsing")

    def exitPrograma(self, ctx:compiladorParser.ProgramaContext):
        print("Fin del parsing")

    def enterIwhile(self, ctx:compiladorParser.IwhileContext):
        print("  "*self.indent + "Comienza while")
        self.indent += 1

    def exitIwhile(self, ctx:compiladorParser.IwhileContext):
        self.indent -= 1
        print("  "*self.indent + "Fin while")

    def enterDeclaracion(self, ctx:compiladorParser.DeclaracionContext):
        self.declaracion += 1
        print("Declaracion ENTER -> |" + ctx.getText() + "|")
        print("  -- Cant. hijos = " + str(ctx.getChildCount()))
    
    def exitDeclaracion(self, ctx:compiladorParser.DeclaracionContext):
        print("Declaracion EXIT  -> |" + ctx.getText() + "|")
        print("  -- Cant. hijos = " + str(ctx.getChildCount()))
        
        # Obtenemos el tipo (hijo 0)
        tipo = ctx.tipo().getText() if ctx.tipo() else None
        #ctx.getChild(0).getText()
        # Lista para almacenar todas las variables declaradas
        variables = []
        
        # Primera variable: ID (hijo 1)
        primer_id = ctx.ID()
        #ctx.getChild(1).getText()
        if primer_id:
            nombre = primer_id.getText()
            # inic (hijo 2): puede ser vacío o ASIG opal
            tiene_inic = ctx.inic() is not None and ctx.inic().ASIG() is not None
            variables.append((nombre, tiene_inic))
        
        # Procesar listavar (hijo 3)
        def procesar_listavar(listavar_ctx):
            if listavar_ctx is None or listavar_ctx.getChildCount() == 0:
                return []
            
            vars_list = []
            # listavar : COMA ID inic listavar
            if listavar_ctx.ID():
                nombre = listavar_ctx.ID().getText()
                # inic puede ser vacío o ASIG opal
                tiene_inic = listavar_ctx.inic() is not None and listavar_ctx.inic().ASIG() is not None
                vars_list.append((nombre, tiene_inic))
                
                # Procesar el siguiente listavar (recursivo)
                siguiente_listavar = listavar_ctx.listavar()
                if siguiente_listavar:
                    vars_list.extend(procesar_listavar(siguiente_listavar))
            
            return vars_list
        
        # Agregar el resto de las variables desde listavar
        listavar_ctx = ctx.listavar()
        variables.extend(procesar_listavar(listavar_ctx))
        
        # Registrar cada variable en la tabla de símbolos
        for nombre, inicializado in variables:
            # Buscar solo en el contexto actual (mismo scope)
            simbolo_existente = self.ts.contextoActual().buscarSimboloLocal(nombre)
            if simbolo_existente:
                print(f"ERROR semantico: Variable '{nombre}' ya declarada en el mismo contexto")
            else:
                # Crear objeto ID con toda la información
                idobj = ID(nombre=nombre, tipo=tipo, inicializado=inicializado, usado=False)
                self.ts.addSimbolo(idobj)
                print(f"Declarada variable '{nombre}' (tipo={tipo}, inicializada={inicializado})")

    def enterListavar(self, ctx:compiladorParser.ListavarContext):
        self.profundidad += 1

    def exitListavar(self, ctx:compiladorParser.ListavarContext):
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
    
    def enterBloque(self, ctx):
        print("  " * self.indent + "Entrando a bloque")
        self.ts.addContexto("bloque")
        self.indent += 1 
    
    def exitBloque(self, ctx):
        self.indent -= 1
        print("  " * self.indent + "Saliendo de bloque")
        self.ts.delContexto()  # POP: Elimina el tope
    
    
    def __str__(self):
        return "Se hicieron " + str(self.declaracion) + " declaraciones\n" + \
                "Se visitaron " + str(self.numNodos) + " nodos"