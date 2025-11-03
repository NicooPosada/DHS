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
        
        # NUEVO: Verificar variables no usadas
        print("\n" + "="*60)
        print("ANÁLISIS DE USO DE VARIABLES")
        print("="*60)
        
        hay_no_usadas = False
        for contexto in self.ts.contextos:
            for nombre, simbolo in contexto.simbolos.items():
                if not simbolo.usado:
                    print(f"WARNING SEMÁNTICO: Variable '{nombre}' declarada pero nunca usada")
                    hay_no_usadas = True
        
        if not hay_no_usadas:
            print("✓ Todas las variables declaradas fueron usadas")
        
        # Tabla de símbolos
        print("\n" + "="*60)
        print("TABLA DE SÍMBOLOS")
        print("="*60)
        print(self.ts)

    def enterIwhile(self, ctx:compiladorParser.IwhileContext):
        print("  "*self.indent + "Comienza while")
        self.indent += 1

    def exitIwhile(self, ctx:compiladorParser.IwhileContext):
        self.indent -= 1
        print("  "*self.indent + "Fin while")
    
    def enterIfor(self, ctx:compiladorParser.IforContext):
        print("  "*self.indent + "Comienza for")
        self.indent += 1

    def exitIfor(self, ctx:compiladorParser.IforContext):
        self.indent -= 1
        print("  "*self.indent + "Fin for")

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
                
                # NUEVO: Verificar compatibilidad de tipos si hay inicialización
                if inicializado and nombre == primer_id.getText():
                    # Verificamos la primera variable (la que usa ctx.inic())
                    if ctx.inic() and ctx.inic().opal():
                        tipo_valor = self.inferir_tipo_expresion(ctx.inic().opal())
                        if tipo_valor:
                            self.verificar_compatibilidad_tipos(tipo, tipo_valor, nombre, ctx.start.line)

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
    
    def exitAsignacion(self, ctx: compiladorParser.AsignacionContext):
       
        nombre_var = None
        
        # Detectar el tipo de asignación y extraer el nombre de la variable
        if ctx.ID():
            nombre_var = ctx.ID().getText()
        
        if nombre_var:
            # Buscar la variable en TODOS los contextos (de actual hacia global)
            simbolo = self.ts.buscarSimbolo(nombre_var)
            
            if simbolo is None:
                # ERROR SEMÁNTICO: Variable usada sin declarar
                print(f"ERROR SEMÁNTICO: Variable '{nombre_var}' usada sin declarar (línea {ctx.start.line})")
            else:
                # Variable encontrada: marcarla como usada
                simbolo.setUsado(True)
                
                # Si es asignación normal (ID = opal), marcarla como inicializada
                if ctx.ASIG() and ctx.opal():
                    simbolo.setInicializado(True)
    
    def exitFactor(self, ctx: compiladorParser.FactorContext):
       
        if ctx.ID():
            nombre_var = ctx.ID().getText()
            
            # Buscar la variable en TODOS los contextos
            simbolo = self.ts.buscarSimbolo(nombre_var)
            
            if simbolo is None:
                # ERROR SEMÁNTICO: Variable usada sin declarar
                print(f"ERROR SEMÁNTICO: Variable '{nombre_var}' usada sin declarar (línea {ctx.start.line})")
            else:
                # Variable encontrada: marcarla como usada
                simbolo.setUsado(True)
                
                # NUEVO: Verificar si está inicializada
                if not simbolo.inicializado:
                    print(f"WARNING SEMÁNTICO: Variable '{nombre_var}' usada sin inicializar (línea {ctx.start.line})")
    
    # ===== FUNCIONES PARA VERIFICACIÓN DE TIPOS =====
    
    def verificar_compatibilidad_tipos(self, tipo_declarado, tipo_valor, nombre, linea):
        """
        Verifica compatibilidad entre tipo declarado y tipo del valor.
        - int <- double: ERROR (pérdida de precisión)
        - double <- int: WARNING (conversión implícita permitida)
        """
        if tipo_valor is None:
            return  # No se pudo inferir el tipo
        
        if tipo_declarado == "int" and tipo_valor == "double":
            print(f"ERROR SEMÁNTICO: No se puede asignar 'double' a variable 'int' '{nombre}' (línea {linea})")
        elif tipo_declarado == "double" and tipo_valor == "int":
            print(f" WARNING: Conversión implícita de 'int' a 'double' en variable '{nombre}' (línea {linea})")
    
    def inferir_tipo_expresion(self, opal_ctx):
        """Infiere el tipo de una expresión desde opal"""
        if opal_ctx is None:
            return None
        if opal_ctx.exp():
            return self.inferir_tipo_exp(opal_ctx.exp())
        return None
    
    def inferir_tipo_exp(self, exp_ctx):
        """Infiere tipo desde exp -> term e"""
        if exp_ctx is None:
            return None
        
        # Verificar el term principal
        if exp_ctx.term():
            tipo_term = self.inferir_tipo_term(exp_ctx.term())
            if tipo_term == "double":
                return "double"  # Si hay un double, toda la expresión es double
            
            # Verificar operaciones adicionales
            if exp_ctx.e():
                tipo_e = self.inferir_tipo_e(exp_ctx.e())
                if tipo_e == "double":
                    return "double"
            
            return tipo_term
        return None
    
    def inferir_tipo_e(self, e_ctx):
        """Infiere tipo desde e (suma/resta recursiva)"""
        if e_ctx is None or e_ctx.getChildCount() == 0:
            return None
        
        if e_ctx.term():
            tipo_term = self.inferir_tipo_term(e_ctx.term())
            if tipo_term == "double":
                return "double"
            
            # Revisar recursivamente
            if e_ctx.e():
                tipo_e_rec = self.inferir_tipo_e(e_ctx.e())
                if tipo_e_rec == "double":
                    return "double"
            
            return tipo_term
        return None
    
    def inferir_tipo_term(self, term_ctx):
        """Infiere tipo desde term -> factor t"""
        if term_ctx is None:
            return None
        
        if term_ctx.factor():
            tipo_factor = self.inferir_tipo_factor(term_ctx.factor())
            if tipo_factor == "double":
                return "double"
            
            # Verificar operaciones adicionales
            if term_ctx.t():
                tipo_t = self.inferir_tipo_t(term_ctx.t())
                if tipo_t == "double":
                    return "double"
            
            return tipo_factor
        return None
    
    def inferir_tipo_t(self, t_ctx):
        """Infiere tipo desde t (multiplicación/división recursiva)"""
        if t_ctx is None or t_ctx.getChildCount() == 0:
            return None
        
        if t_ctx.factor():
            tipo_factor = self.inferir_tipo_factor(t_ctx.factor())
            if tipo_factor == "double":
                return "double"
            
            # Revisar recursivamente
            if t_ctx.t():
                tipo_t_rec = self.inferir_tipo_t(t_ctx.t())
                if tipo_t_rec == "double":
                    return "double"
            
            return tipo_factor
        return None
    
    def inferir_tipo_factor(self, factor_ctx):
        """
        Infiere tipo desde factor.
        Retorna 'int', 'double' o None.
        """
        if factor_ctx is None:
            return None
        
        # Caso 1: NUMERO_CON_PUNTO (3.14) -> double
        if factor_ctx.NUMERO_CON_PUNTO():
            return "double"
        
        # Caso 2: NUMERO (5) -> int
        if factor_ctx.NUMERO():
            return "int"
        
        # Caso 3: ID (variable) -> buscar su tipo en la tabla
        if factor_ctx.ID() and factor_ctx.CA() is None:  # No es array
            nombre_var = factor_ctx.ID().getText()
            simbolo = self.ts.buscarSimbolo(nombre_var)
            if simbolo:
                return simbolo.tipo
            return None
        
        # Caso 4: Expresión entre paréntesis -> recursivo
        if factor_ctx.exp():
            return self.inferir_tipo_exp(factor_ctx.exp())
        
        return None
    
    
    def __str__(self):
        return "Se hicieron " + str(self.declaracion) + " declaraciones\n" + \
                "Se visitaron " + str(self.numNodos) + " nodos"