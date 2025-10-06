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
        #Obtenemos el tipo:
        #El ctx.tipo nos va a devolver el nodo del arbol
        #que representa el tipo(int, float, double, etc)
        #y el .getText nos va devolver el texto
        tipo = ctx.tipo().getText() if ctx.tipo() else None
        
        #Obtenemos la lista de declaradores
        #Esto es porque podemos tener multiples declaraciones
        #devuelve el nodo que contiene todos los declaradores
        lista_declaradores = ctx.listaDeclaradores()
        if lista_declaradores is None:
            return
        
        #Extraemos los nombres de las variables declaradas
        names = [] #Creamos la lista de nombre de variables
        inicializados = {}#Creamos este diccionario para saber cuales estan inicializados
        
        #Obtenemos todos los declaradores:
        #declarador() puede devolver una lista o uno solo
        decls = lista_declaradores.declarador()
        if not isinstance(decls, list):
            decls = [decls] #SI es uno SOLO, lo comvertimos a lista
            
        #Procesamos los declaradores, obtenemos los tokens
        for d in decls:
            #Obtenemos el ID (osea el nombre de la variable)
            id_token = d.ID() if hasattr(d,'ID') else None
            if id_token:
                name = id_token.getText()
                names.append(name)
                
                #Verificamos si tiene inicializacion
                # Recorre los hijos del declarador buscando el símbolo '='
                tiene_asig = any(child.getText() == '=' for child in d.getChildren()) if hasattr (d, 'getChildren') else False
                inicializados[name] = tiene_asig
                
        #Registrar cada  nombre en la tabla de simbolos
        for n in names:
            #Buscamos solo en el conexto actual
            simbolo_existente = self.ts.contextoActual().buscarSimboloLocal(n)
            if simbolo_existente:
                print(f"Error semantico(se declaro la misma variable en el mismo contexto)")
            else:
                
                #Creamos objeto ID con toda la informacion para guardar la variable declarada
                idobj = ID(nombre=n, tipo=tipo, inicializado=inicializados.get(n, False), usado=False)
                self.ts.addSimbolo(idobj)
                print(f"Declarada variable '{n}' tipo={tipo}, inicializada={inicializados.get(n, False)}")
    def enterListaAsignaciones(self, ctx:compiladorParser.ListaAsignacionesContext):
        self.profundidad += 1

    def exitListaAsignaciones(self, ctx:compiladorParser.ListaAsignacionesContext):
        print("  -- ListaAsignaciones(%d) Cant. hijos  = %d" % (self.profundidad, ctx.getChildCount()))
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