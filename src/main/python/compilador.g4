grammar compilador;

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
RETURN : 'retorn' ;

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

programa : instrucciones EOF ;

instrucciones : instruccion instrucciones
              |
              ;

instruccion : asignacion
            | declaracion
            | retorno
            | iif
            | ifor
            | iwhile
            | bloque
            ;

bloque : LLA instrucciones LLC ;

iwhile : WHILE PA opal PC instruccion ;

iif : IF PA opal PC instruccion ielse ;

ielse : ELSE instruccion
      |
      ;

ifor :  FOR PA PYC PYC PC instruccion ;

declaracion : tipo ID listavar PYC ;

listavar : COMA ID listavar
          |
          ;

tipo : INT
     | DOUBLE
     ;

asignacion : ID ASIG opal PYC ;

opal : NUMERO
     | ID
     ;

retorno : RETURN codigo PYC ;
codigo : NUMERO;
