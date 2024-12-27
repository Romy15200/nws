%{
#include "smv_parser.h"
#include "smv_typecheck.h"

#include <util/mathematical_types.h>
#include <util/std_expr.h>
#include <util/std_types.h>

#define YYSTYPE unsigned
#define PARSER (*smv_parser_ptr)

#include "smv_y.tab.h"

#define YYMAXDEPTH 200000
#define YYSTYPE_IS_TRIVIAL 1

/*------------------------------------------------------------------------*/

#define yylineno yysmvlineno
#define yytext yysmvtext

#define yyerror yysmverror
int yysmverror(const std::string &error);
int yylex();
extern char *yytext;

/*------------------------------------------------------------------------*/

#define mto(x, y) stack_expr(x).add_to_operands(std::move(stack_expr(y)))

  /*******************************************************************\

  Function: init

    Inputs:

   Outputs:

   Purpose:

  \*******************************************************************/

  static void init(exprt & expr) {
    expr.clear();
    PARSER.set_source_location(expr);
}

/*******************************************************************\

Function: init

  Inputs:

 Outputs:

 Purpose:

\*******************************************************************/

static void init(YYSTYPE &expr)
{
  newstack(expr);
  init(stack_expr(expr));
}

/*******************************************************************\

Function: init

  Inputs:

 Outputs:

 Purpose:

\*******************************************************************/

 static void init(YYSTYPE &expr, const irep_idt &id)
{
  init(expr);
  stack_expr(expr).id(id);
}

 /// binary TODO[docu]
 static void binary(YYSTYPE & x_result, YYSTYPE & y_lhs, const irep_idt &id,
                    YYSTYPE &z_rhs, const typet &t)
 {
   init(x_result, id);
   stack_expr(x_result).type() = t;
   auto &lhs = stack_expr(y_lhs);
   auto &rhs = stack_expr(z_rhs);
   stack_expr(x_result).add_to_operands(std::move(lhs), std::move(rhs));
 }

 /// binary TODO[docu]
 static void binary_arith(YYSTYPE & x_result, YYSTYPE & y_lhs,
                          const irep_idt &id, YYSTYPE &z_rhs)
 {
   init(x_result, id);
   auto &lhs = stack_expr(y_lhs);
   DATA_INVARIANT(lhs.type().id() != ID_nil, "arith expr without lhs type");
   stack_expr(x_result).type() = lhs.type();
   auto &rhs = stack_expr(z_rhs);
   stack_expr(x_result).add_to_operands(std::move(lhs), std::move(rhs));
 }

 /*******************************************************************\

 Function: j_binary

   Inputs:

  Outputs:

  Purpose:

 \*******************************************************************/

 static void j_binary(YYSTYPE & dest, YYSTYPE & op1, const irep_idt &id,
                      YYSTYPE &op2, const typet &t) {
   if (stack_expr(op1).id() == id) {
     dest = op1;
     mto(dest, op2);
   } else if (stack_expr(op2).id() == id) {
     dest = op2;
     mto(dest, op1);
   } else
     binary(dest, op1, id, op2, t);
}

/*******************************************************************\

Function: new_module

  Inputs:

 Outputs:

 Purpose:

\*******************************************************************/

static void new_module(YYSTYPE &module)
{
  const std::string name=smv_module_symbol(stack_expr(module).id_string());
  PARSER.module=&PARSER.parse_tree.modules[name];
  PARSER.module->name=name;
  PARSER.module->base_name=stack_expr(module).id_string();
}

/*------------------------------------------------------------------------*/

%}

%token AG_Token AX_Token AF_Token EG_Token EX_Token EF_Token

%token G_Token X_Token F_Token R_Token U_Token

%token INIT_Token TRANS_Token SPEC_Token LTLSPEC_Token VAR_Token DEFINE_Token ASSIGN_Token
%token INVAR_Token FAIRNESS_Token MODULE_Token ARRAY_Token OF_Token
%token DOTDOT_Token BOOLEAN_Token EXTERN_Token

%token NEXT_Token INC_Token DEC_Token CASE_Token ESAC_Token BECOMES_Token
%token ADD_Token SUB_Token SWITCH_Token init_Token PLUS_Token

%token STRING_Token QSTRING_Token QUOTE_Token
%token NUMBER_Token FALSE_Token TRUE_Token

/* operator precedence, low to high */
%right IMPLIES_Token
%left  EQUIV_Token
%left  IF_Token
%left  XOR_Token
%left  OR_Token
%left  AND_Token
%left  NOT_Token
%left  EX_Token AX_Token EF_Token AF_Token EG_Token AG_Token E_Token A_Token U_Token R_Token F_Token G_Token X_Token
%left  EQUAL_Token NOTEQUAL_Token LT_Token GT_Token LE_Token GE_Token
%left  UNION_Token
%left  IN_Token NOTIN_Token
%left  MOD_Token /* Precedence from CMU SMV, different from NuSMV */
%left  PLUS_Token MINUS_Token
%left  TIMES_Token DIVIDE_Token
%left  UMINUS           /* supplies precedence for unary minus */
%left  DOT_Token

%%

start      : modules
           | SPEC_Token formula { PARSER.parse_tree.formula = stack_expr($1); }
           ;

modules    : module
           | modules module
           ;

module     : module_head sections
           ;

module_name: STRING_Token
           | QUOTE_Token
           ;

module_head: MODULE_Token module_name { new_module($2); }
           | MODULE_Token module_name { new_module($2); } '(' module_argument_list_opt ')'
           ;

sections   : /* epsilon */
           | sections section
           ;
           
semi_opt   :    /* empty */
           | ';'
           ;

section    : VAR_Token vardecls
           | VAR_Token
           | INIT_Token formula semi_opt { PARSER.module->add_init(stack_expr($2), stack_expr($1).source_location()); }
           | INIT_Token
           | TRANS_Token formula semi_opt { PARSER.module->add_trans(stack_expr($2), stack_expr($1).source_location()); }
           | TRANS_Token
           | SPEC_Token formula semi_opt { PARSER.module->add_ctlspec(stack_expr($2), stack_expr($1).source_location()); }
           | SPEC_Token
           | LTLSPEC_Token formula semi_opt { PARSER.module->add_ltlspec(stack_expr($2), stack_expr($1).source_location()); }
           | LTLSPEC_Token
           | ASSIGN_Token assignments
           | ASSIGN_Token
           | DEFINE_Token defines
           | DEFINE_Token
           | INVAR_Token formula semi_opt { PARSER.module->add_invar(stack_expr($2), stack_expr($1).source_location()); }
           | INVAR_Token
           | FAIRNESS_Token formula semi_opt { PARSER.module->add_fairness(stack_expr($2), stack_expr($1).source_location()); }
           | FAIRNESS_Token
           | EXTERN_Token extern_var semi_opt
           | EXTERN_Token
           ;
 
extern_var : variable_name EQUAL_Token QUOTE_Token
           {
             const irep_idt &identifier=stack_expr($1).get(ID_identifier);
             smv_parse_treet::mc_vart &var=PARSER.module->vars[identifier];

             if(var.identifier!=irep_idt())
             {
               yyerror("variable `"+id2string(identifier)+"' already declared extern");
               YYERROR;
             }
             else
               var.identifier=stack_expr($3).id_string();
           }
           ;

vardecls   : vardecl
           | vardecls vardecl
           ;

module_argument: variable_name
           {
             const irep_idt &identifier=stack_expr($1).get(ID_identifier);
             smv_parse_treet::mc_vart &var=PARSER.module->vars[identifier];
             var.var_class=smv_parse_treet::mc_vart::ARGUMENT;
             PARSER.module->ports.push_back(identifier);
           }
           ;

module_argument_list: module_argument
           | module_argument_list ',' module_argument
           ;

module_argument_list_opt: /* empty */
           | module_argument_list
           ;

type       : ARRAY_Token NUMBER_Token DOTDOT_Token NUMBER_Token OF_Token type
           {
             init($$, ID_array);
             int start=atoi(stack_expr($2).id().c_str());
             int end=atoi(stack_expr($4).id().c_str());

             if(end < start)
             {
               yyerror("array must end with number >= `"+std::to_string(start)+"'");
               YYERROR;
             }

             stack_type($$).set(ID_size, end-start+1);
             stack_type($$).set(ID_offset, start);
             stack_type($$).add_subtype()=stack_type($6);
           }
           | BOOLEAN_Token { init($$, ID_bool); }
           | '{' enum_list '}' { $$=$2; }
           | NUMBER_Token DOTDOT_Token NUMBER_Token
           {
             init($$, ID_range);
             stack_type($$).set(ID_from, stack_expr($1));
             stack_type($$).set(ID_to, stack_expr($3));
           }
           | usertype
           ;

usertype   : module_name
           {
             init($$, "submodule");
             stack_expr($$).set(ID_identifier,
                           smv_module_symbol(stack_expr($1).id_string()));
           }
           | module_name '(' formula_list ')'
           {
             init($$, "submodule");
             stack_expr($$).set(ID_identifier,
                           smv_module_symbol(stack_expr($1).id_string()));
             stack_expr($$).operands().swap(stack_expr($3).operands());
           }
           ;

enum_list  : enum_element
           {
             init($$, ID_enumeration);
             stack_expr($$).add(ID_elements).get_sub().push_back(irept(stack_expr($1).id()));
           }
           | enum_list ',' enum_element
           {
             $$=$1;
             stack_expr($$).add(ID_elements).get_sub().push_back(irept(stack_expr($3).id())); 
           }
           ;

enum_element: STRING_Token
           {
             $$=$1;
             PARSER.module->enum_set.insert(stack_expr($1).id_string());
           }
           ;

vardecl    : variable_name ':' type ';'
{
  const irep_idt &identifier=stack_expr($1).get(ID_identifier);
  smv_parse_treet::mc_vart &var=PARSER.module->vars[identifier];

  switch(var.var_class)
  {
  case smv_parse_treet::mc_vart::UNKNOWN:
    var.type=(typet &)stack_expr($3);
    var.var_class=smv_parse_treet::mc_vart::DECLARED;
    break;

  case smv_parse_treet::mc_vart::DEFINED:
    yyerror("variable `"+id2string(identifier)+"' already defined");
    YYERROR;
    break;

  case smv_parse_treet::mc_vart::DECLARED:
    yyerror("variable `"+id2string(identifier)+"' already declared as variable");
    YYERROR;
    break;
  
  case smv_parse_treet::mc_vart::ARGUMENT:
    yyerror("variable `"+id2string(identifier)+"' already declared as argument");
    YYERROR;
    break;
  
  default:
    DATA_INVARIANT(false, "unexpected variable class");
  }
}
           ;

assignments: assignment
           | assignments assignment
           ;

assignment : assignment_head '(' assignment_var ')' BECOMES_Token formula ';'
           {
             exprt lhs = unary_exprt{stack_expr($1).id(), std::move(stack_expr($3))};
             PARSER.module->add_assign(binary_exprt{lhs, ID_equal, stack_expr($6)});
           }
           | assignment_var BECOMES_Token formula ';'
           {
             exprt lhs = unary_exprt{ID_smv_assign_current, std::move(stack_expr($1))};
             PARSER.module->add_assign(binary_exprt{lhs, ID_equal, stack_expr($3)});
           }
           ;

assignment_var: variable_name
           ;

assignment_head: init_Token { init($$, ID_smv_assign_init); }
               | NEXT_Token { init($$, ID_smv_assign_next); }
               ;

defines:     define
           | defines define
           ;

define     : assignment_var BECOMES_Token formula ';'
{
  const irep_idt &identifier=stack_expr($1).get(ID_identifier);
  smv_parse_treet::mc_vart &var=PARSER.module->vars[identifier];

  switch(var.var_class)
  {
  case smv_parse_treet::mc_vart::UNKNOWN:
    var.type.make_nil();
    var.var_class=smv_parse_treet::mc_vart::DEFINED;
    break;

  case smv_parse_treet::mc_vart::DECLARED:
    var.var_class=smv_parse_treet::mc_vart::DEFINED;
    break;

  case smv_parse_treet::mc_vart::DEFINED:
    yyerror("variable `"+id2string(identifier)+"' already defined");
    YYERROR;
    break;
  
  case smv_parse_treet::mc_vart::ARGUMENT:
    yyerror("variable `"+id2string(identifier)+"' already declared as argument");
    YYERROR;
    break;
  
  default:
    DATA_INVARIANT(false, "unexpected variable class");
  }

  binary($$, $1, ID_equal, $3, bool_typet{});
  PARSER.module->add_define(stack_expr($$));
}
;

formula    : term
           ;

term       : variable_name
           | NEXT_Token '(' term ')'  { init($$, ID_smv_next); mto($$, $3); }
           | '(' formula ')'          { $$=$2; }
           | '{' formula_list '}'     { $$=$2; stack_expr($$).id("smv_nondet_choice"); }
           | INC_Token '(' term ')'   { init($$, "inc"); mto($$, $3); }
           | DEC_Token '(' term ')'   { init($$, "dec"); mto($$, $3); }
           | ADD_Token '(' term ',' term ')' { j_binary($$, $3, ID_plus, $5, stack_expr($5).type()); }
           | SUB_Token '(' term ',' term ')' { init($$, ID_minus); mto($$, $3); mto($$, $5); }
           | NUMBER_Token             { init($$, ID_constant); stack_expr($$).set(ID_value, stack_expr($1).id()); stack_expr($$).type()=integer_typet(); }
           | TRUE_Token               { init($$, ID_constant); stack_expr($$).set(ID_value, ID_true); stack_expr($$).type()=typet(ID_bool); }
           | FALSE_Token              { init($$, ID_constant); stack_expr($$).set(ID_value, ID_false); stack_expr($$).type()=typet(ID_bool); }
           | CASE_Token cases ESAC_Token { $$=$2; }
           | term IF_Token term ':' term %prec IF_Token
                                      { init($$, ID_if); mto($$, $1); mto($$, $3); mto($$, $5); }
           | SWITCH_Token '(' variable_name ')' '{' switches '}' { init($$, ID_switch); mto($$, $3); mto($$, $6); }
           | MINUS_Token term %prec UMINUS
                                      { init($$, ID_unary_minus); mto($$, $2); }
           | term MOD_Token term      { binary_arith($$, $1, ID_mod, $3); }
           | term TIMES_Token term    { binary_arith($$, $1, ID_mult, $3); }
           | term DIVIDE_Token term   { binary_arith($$, $1, ID_div, $3); }
           | term PLUS_Token term     { binary_arith($$, $1, ID_plus, $3); }
           | term MINUS_Token term    { binary_arith($$, $1, ID_minus, $3); }
           | term EQUIV_Token term    { binary($$, $1, ID_smv_iff, $3, bool_typet{}); }
           | term IMPLIES_Token term  { binary($$, $1, ID_implies, $3, bool_typet{}); }
           | term XOR_Token term      { j_binary($$, $1, ID_xor, $3, bool_typet{}); }
           | term OR_Token term       { j_binary($$, $1, ID_or, $3, bool_typet{}); }
           | term AND_Token term      { j_binary($$, $1, ID_and, $3, bool_typet{}); }
           | NOT_Token term           { init($$, ID_not); mto($$, $2); }
           | AX_Token  term           { init($$, ID_AX);  mto($$, $2); }
           | AF_Token  term           { init($$, ID_AF);  mto($$, $2); }
           | AG_Token  term           { init($$, ID_AG);  mto($$, $2); }
           | EX_Token  term           { init($$, ID_EX);  mto($$, $2); }
           | EF_Token  term           { init($$, ID_EF);  mto($$, $2); }
           | EG_Token  term           { init($$, ID_EG);  mto($$, $2); }
           | A_Token '[' term U_Token term ']' { binary($$, $3, ID_AU, $5, bool_typet{}); }
           | A_Token '[' term R_Token term ']' { binary($$, $3, ID_AR, $5, bool_typet{}); }
           | E_Token '[' term U_Token term ']' { binary($$, $3, ID_EU, $5, bool_typet{}); }
           | E_Token '[' term R_Token term ']' { binary($$, $3, ID_ER, $5, bool_typet{}); }
           | F_Token  term            { init($$, ID_F);  mto($$, $2); }
           | G_Token  term            { init($$, ID_G);  mto($$, $2); }
           | X_Token  term            { init($$, ID_X);  mto($$, $2); }
           | term U_Token term        { binary($$, $1, ID_U, $3, bool_typet{}); }
           | term R_Token term        { binary($$, $1, ID_R, $3, bool_typet{}); }
           | term EQUAL_Token    term { binary($$, $1, ID_equal,  $3, bool_typet{}); }
           | term NOTEQUAL_Token term { binary($$, $1, ID_notequal, $3, bool_typet{}); }
           | term LT_Token       term { binary($$, $1, ID_lt,  $3, bool_typet{}); }
           | term LE_Token       term { binary($$, $1, ID_le, $3, bool_typet{}); }
           | term GT_Token       term { binary($$, $1, ID_gt,  $3, bool_typet{}); }
           | term GE_Token       term { binary($$, $1, ID_ge, $3, bool_typet{}); }
           | term UNION_Token    term { binary($$, $1, ID_smv_union, $3, bool_typet{}); }
           | term IN_Token       term { binary($$, $1, ID_smv_setin, $3, bool_typet{}); }
           | term NOTIN_Token    term { binary($$, $1, ID_smv_setnotin, $3, bool_typet{}); }
           ;

formula_list: formula { init($$); mto($$, $1); }
            | formula_list ',' formula { $$=$1; mto($$, $3); }
            ;

variable_name: qstring_list
           {
             const irep_idt &id=stack_expr($1).id();

             bool is_enum=(PARSER.module->enum_set.find(id)!=
                           PARSER.module->enum_set.end());
             bool is_var=(PARSER.module->vars.find(id)!=
                          PARSER.module->vars.end());

             if(is_var && is_enum)
             {
               yyerror("identifier `"+id2string(id)+"' is ambiguous");
               YYERROR;
             }
             else if(is_enum)
             {
               init($$, ID_constant);
               stack_expr($$).type()=typet(ID_enumeration);
               stack_expr($$).set(ID_value, id);
             }
             else // not an enum, probably a variable
             {
               init($$, ID_symbol);
               stack_expr($$).set(ID_identifier, id);
               auto var_it = PARSER.module->vars.find(id);
               if(var_it!= PARSER.module->vars.end())
                 stack_expr($$).type()=var_it->second.type;
               //PARSER.module->vars[stack_expr($1).id()];
             }
           }
           | QUOTE_Token
           {
             const irep_idt &id=stack_expr($1).id();

             init($$, ID_symbol);
             stack_expr($$).set(ID_identifier, id);
             PARSER.module->vars[id];
           }
           ;

qstring_list: QSTRING_Token
           {
             init($$, std::string(stack_expr($1).id_string(), 1)); // remove backslash
           }
           | STRING_Token
           | qstring_list DOT_Token QSTRING_Token
           {
             std::string id(stack_expr($1).id_string());
             id+=".";
             id+=std::string(stack_expr($3).id_string(), 1); // remove backslash
             init($$, id);
           }
           | qstring_list DOT_Token STRING_Token
           {
             std::string id(stack_expr($1).id_string());
             id+=".";
             id+=stack_expr($3).id_string();
             init($$, id);
           }
           | qstring_list '[' NUMBER_Token ']'
           {
             std::string id(stack_expr($1).id_string());
             id+="[";
             id+=stack_expr($3).id_string();
             id+="]";
             init($$, id);
           }
           | qstring_list '(' NUMBER_Token ')'
           {
             std::string id(stack_expr($1).id_string());
             id+="(";
             id+=stack_expr($3).id_string();
             id+=")";
             init($$, id);
           }
           ;

cases      :
           { init($$, "smv_cases"); }
           | cases case
           { $$=$1; mto($$, $2); }
           ;

case       : formula ':' formula ';'
           { binary($$, $1, ID_case, $3, stack_expr($3).type()); }
           ;

switches   :
           { init($$, "switches"); }
           | switches switch
           { $$=$1; mto($$, $2); }
           ;

switch     : NUMBER_Token ':' term ';'
           { init($$, ID_switch); mto($$, $1); mto($$, $3); }
           ;

%%

int yysmverror(const std::string &error)
{
  PARSER.parse_error(error, yytext);
  return 0;
}

#undef yyerror

