class ID:
    """Representa un símbolo (variable o función simple)."""
    def __init__(self, nombre: str, tipo: str = None, inicializado: bool = False, usado: bool = False):
        self.nombre = nombre
        self.tipo = tipo
        self.inicializado = inicializado
        self.usado = usado

    def setInicializado(self, val=True):
        self.inicializado = val

    def setUsado(self, val=True):
        self.usado = val

    def __repr__(self):
        return f"ID(nombre={self.nombre}, tipo={self.tipo}, init={self.inicializado}, used={self.usado})"


class Contexto:
    """Contexto (scope) con un diccionario de símbolos."""
    def __init__(self, nombre="<anon>"):
        self.nombre = nombre
        self.simbolos = {}  # nombre -> ID

    def addSimbolo(self, id_obj: ID):
        if id_obj.nombre in self.simbolos:
            return False  # ya existe en este contexto
        self.simbolos[id_obj.nombre] = id_obj
        return True

    def buscarSimboloLocal(self, nombre: str):
        return self.simbolos.get(nombre)


class TS:
    """Singleton: tabla de símbolos con pila de contextos."""
    _instancia = None

    def __init__(self):
        self.contextos = []
        # crear contexto global por defecto
        self.addContexto("global")

    @classmethod
    def getTablaSimbolo(cls):
        if cls._instancia is None:
            cls._instancia = TS()
        return cls._instancia

    def addContexto(self, nombre="anon"):
        ctx = Contexto(nombre)
        self.contextos.append(ctx)
        return ctx

    def delContexto(self):
        if len(self.contextos) > 1:  # opcional: no retirar el global
            return self.contextos.pop()
        return None

    def contextoActual(self):
        return self.contextos[-1]

    def addSimbolo(self, id_obj: ID):
        return self.contextoActual().addSimbolo(id_obj)

    def buscarSimbolo(self, nombre: str):
        # buscar desde el contexto actual hacia afuera (LIFO)
        for ctx in reversed(self.contextos):
            s = ctx.buscarSimboloLocal(nombre)
            if s is not None:
                return s
        return None

    def __repr__(self):
        out = []
        for i, ctx in enumerate(self.contextos):
            out.append(f"Context[{i}] '{ctx.nombre}': {list(ctx.simbolos.values())}")
        return "\n".join(out)
