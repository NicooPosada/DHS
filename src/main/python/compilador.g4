grammar compilador;

//Repositorio: https://github.com/NicooPosada/DHS

// ===== TOKENS LEXICOS =====
fragment LETRA : [A-Za-z] ;
fragment DIGITO : [0-9] ;

// Símbolos
PA : '(' ;
PC : ')' ;
LLA : '{' ;
LLC : '}' ;
PYC : ';' ;
ASIG : '=' ;
CA : '[' ;
CC : ']' ;
SUMA : '+' ;
RESTA : '-' ;
MULT : '*' ;
DIV : '/' ;
COMA : ',' ;
MENOR : '<' ;
MAYOR : '>' ;
MENORIGUAL : '<=' ;
MAYORIGUAL : '>=' ;
IGUAL : '==' ;
DIFERENTE : '!=' ;
AND : '&&' ;
OR : '||' ;
NOT : '!' ;
INCREMENT : '++' ;
DECREMENT : '--' ;

// Palabras reservadas
INT : 'int' ;
DOUBLE : 'double' ;
IF : 'if' ;
ELSE : 'else' ;
FOR : 'for' ;
WHILE : 'while' ;
RETURN : 'return' ;

// Literales
NUMERO_CON_PUNTO : ('+' | '-')? DIGITO+ '.' DIGITO+ ;
NUMERO : ('+' | '-')? DIGITO+ ;
ID : (LETRA | '_')(LETRA | DIGITO | '_')* ;
WS : [ \t\r\n] -> skip ;
OTRO : . ;

// ===== ESTRUCTURA GENERAL DEL PROGRAMA =====
programa : instrucciones EOF ;

instrucciones : instruccion instrucciones 
              |
              ;

instruccion : asignacion PYC
           | declaracion
           | iwhile
           | bloque
           | iif
           | ifor
           | declaracionDeFuncion
           | prototipoDeFuncion
           | llamadaFuncionInstruccion
           | retorno
           ;

bloque : LLA instrucciones LLC ;

// ===== TIPOS Y DECLARACIONES =====
tipo : INT
     | DOUBLE
     ;


inic : ASIG opal
     |
     ;

declaracion : tipo ID inic listavar PYC ;

listavar : COMA ID inic listavar
         |
         ;


//declaracion : tipo listaDeclaradores PYC ;

//listaDeclaradores : declarador (COMA declarador)* ;

listaOpal : opal (COMA opal)* ;

//declarador : ID
//           | ID ASIG opal
//           | ID CA NUMERO CC
//           | ID CA NUMERO CC ASIG LLA listaOpal LLC
//           ;

// ===== EXPRESIONES ARITMÉTICAS =====
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
       | ID
       | ID CA opal CC
       | NUMERO_CON_PUNTO
       | NUMERO
       | llamadaFuncion
       ;

// ===== COMPARACIONES =====
comparacion : opal (MENOR | MAYOR | MENORIGUAL | MAYORIGUAL | IGUAL | DIFERENTE) opal ;

// ===== ASIGNACIONES =====
asignacion : ID ASIG opal
           | INCREMENT ID
           | DECREMENT ID
           | ID INCREMENT
           | ID DECREMENT
           ;

           // ===== EXPRESIONES LÓGICAS =====
//expresionLogica : comparacion logica ;
//Cambiamos aca porque no soportaba paréntesis
expresionLogica : comparacion
                | expresionLogica AND expresionLogica
                | expresionLogica OR expresionLogica
                | PA expresionLogica PC
                ;

//logica : AND comparacion logica
//       | OR comparacion logica
//       |
//       ;


listaAsignaciones : asignacion (COMA asignacion)* 
                  |
                  ;



// ===== ESTRUCTURAS DE CONTROL =====

// While
iwhile : WHILE PA expresionLogica PC instruccion ;

// If-Else
iif : IF PA expresionLogica PC instruccion ielse ;
ielse : ELSE instruccion
      | 
      ;

// For
ifor : FOR PA forInit PYC expresionLogica PYC forInc PC bloque ;

forInit : tipo ID inic listavar
        | listaAsignaciones 
        |
        ;

forInc : listaContadores
       |
       ;

listaContadores : asignacion (COMA asignacion)*
                |
                ;

// ===== FUNCIONES =====
prototipoDeFuncion : tipo ID PA parametros PC PYC ;

declaracionDeFuncion : tipo ID PA parametros PC bloque ;


llamadaFuncion : ID PA argumentos PC;

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

llamadaFuncionInstruccion : llamadaFuncion PYC;
