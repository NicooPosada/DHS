grammar compilador;

//Repositorio: https://github.com/NicooPosada/DHS

fragment LETRA : [A-Za-z] ;
fragment DIGITO : [0-9] ;

//Simbolos
PA : '(' ;
PC : ')' ;
LLA : '{' ;
LLC : '}' ;
PYC : ';' ;
COMA : ',' ;
ASIG : '=' ;
CA : '[' ;
CC: ']';
SUMA : '+' ;
RESTA : '-' ;
MULT : '*' ;
DIV : '/' ;
MENOR : '<' ;
MAYOR : '>' ;
MENORIGUAL : '<=' ;
MAYORIGUAL : '>=' ;
IGUAL : '==' ;
DIFERENTE : '!=' ;
INCREMENT : '++' ;
DECREMENT : '--' ;
AND : '&&' ;
OR : '||' ;
NOT : '!' ;

//Palabras reservadas
INT : 'int' ;
DOUBLE : 'double' ;
IF : 'if' ;
ELSE : 'else' ;
WHILE : 'while' ;
FOR : 'for' ;
RETURN : 'return' ;


//Literales
NUMERO : ('+' | '-')? DIGITO+ ;

ID : (LETRA | '_')(LETRA | DIGITO | '_')* ;

WS : [ \n\r\t] -> skip ;

OTRO : . ;

// s : ID     {print("ID ->" + $ID.text + "<--") }         s
//   | NUMERO {print("NUMERO ->" + $NUMERO.text + "<--") } s
//   | OTRO   {print("Otro ->" + $OTRO.text + "<--") }     s
//   | EOF
//   ;

// s : PA s PC s
//   |
//   ;

//Estrctura del programa
programa : instrucciones EOF ;

instrucciones : instruccion instrucciones
              |
              ;

instruccion : asignacion PYC
            | declaracion
            | prototipoDeFuncion
            | declaracionDeFuncion
            | llamadaFuncionInstruccion
            | retorno
            | iif
            | ifor
            | iwhile
            | bloque
            ;

bloque : LLA instrucciones LLC ;

//Declaracion
tipo : INT
     | DOUBLE
     ;

declaracion : tipo listaDeclaradores PYC ;

listaDeclaradores : declarador (COMA declarador)* ;

listaOpal : opal (COMA opal)* ;

declarador : ID
           | ID ASIG opal
           | ID CA NUMERO CC
           | ID CA NUMERO CC ASIG LLA listaOpal LLC
           ;

//Expresiones Aritmeticas
opal : exp ;

exp : term e ;

e : SUMA term e
  | RESTA term e
  |
  ;

term : factor t ;

t : MULT factor t
  | DIV factor t
  |
  ;

factor : PA exp PC
       | NUMERO
       | ID CA opal CC
       | ID
       | llamadaFuncion
       ;

//Comparaciones
comparacion : opal (MENOR | MAYOR | MENORIGUAL | MAYORIGUAL | IGUAL | DIFERENTE) opal ;

//Asignaciones
asignacion : ID ASIG opal
           | INCREMENT ID
           | DECREMENT ID
           | ID INCREMENT
           | ID DECREMENT
           ;

//Expresiones Logicas
expresionLogica: comparacion logica ;

logica : AND comparacion logica
       | OR comparacion logica
       |
       ;

listaAsignaciones : asignacion (COMA asignacion)*
                  |
                  ;

//Estructuras de control
iwhile : WHILE PA expresionLogica PC instruccion ;

iif : IF PA expresionLogica PC instruccion ielse ;

ielse : ELSE instruccion
      |
      ;

ifor :  FOR PA forInit PYC expresionLogica PYC forInc PC bloque ;

forInit : listaAsignaciones
        |
        ;

forInc : listaContadores
       |
       ;

listaContadores : asignacion (COMA asignacion)*
                |
                ;

//Funciones
prototipoDeFuncion : tipo ID PA parametros PC PYC ;

declaracionDeFuncion : tipo ID PA parametros PC bloque ;

llamadaFuncion : ID PA argumentos PC ;

retorno : RETURN opal PYC
        | RETURN PYC
        ;

parametro : tipo ID ;

parametros : parametro (COMA parametro)*
           |
           ;

argumentos : opal (COMA opal)*
           |
           ;

llamadaFuncionInstruccion : llamadaFuncion PYC ;
