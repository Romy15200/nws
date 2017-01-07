/*******************************************************************\

Module: Show Transition Relation in various Formats

Author: Daniel Kroening, kroening@kroening.com

\*******************************************************************/

#include <fstream>
#include <iostream>

#include <verilog/expr2verilog.h>

#include "show_trans.h"
#include "ebmc_base.h"
#include "ebmc_version.h"
#include "output_verilog.h"

/*******************************************************************\

   Class: show_trans

 Purpose:

\*******************************************************************/

class show_transt:public ebmc_baset
{
public:
  show_transt(
    const cmdlinet &cmdline,
    ui_message_handlert &ui_message_handler):
    ebmc_baset(cmdline, ui_message_handler)
  {
  }

  int show_trans_verilog_rtl();
  int show_trans_verilog_netlist();
  int show_trans();

protected:
  int show_trans_verilog_rtl(std::ostream &out);
  int show_trans_verilog_netlist(std::ostream &out);
  void verilog_header(std::ostream &out, const std::string &desc);
  void print_verilog_constraints(const exprt &, std::ostream &);
};

/*******************************************************************\

Function: show_trans_verilog_netlist

  Inputs:

 Outputs:

 Purpose:

\*******************************************************************/

int show_trans_verilog_netlist(
  const cmdlinet &cmdline,
  ui_message_handlert &ui_message_handler)
{
  show_transt show_trans(cmdline, ui_message_handler);  
  return show_trans.show_trans_verilog_netlist();
}

/*******************************************************************\

Function: show_trans_verilog_rtl

  Inputs:

 Outputs:

 Purpose:

\*******************************************************************/

int show_trans_verilog_rtl(
  const cmdlinet &cmdline,
  ui_message_handlert &ui_message_handler)
{
  show_transt show_trans(cmdline, ui_message_handler);  
  return show_trans.show_trans_verilog_rtl();
}

/*******************************************************************\

Function: show_transt::show_trans_verilog_netlist

  Inputs:

 Outputs:

 Purpose:

\*******************************************************************/

int show_transt::show_trans_verilog_netlist(std::ostream &out)
{
  output_verilog_netlistt output_verilog(
    symbol_table, out, get_message_handler());

  try
  {
    verilog_header(out, "Verilog netlist");
    output_verilog(*main_symbol);
  }
  
  catch(const std::string &e)
  {
    output_verilog.error() << e << eom;
    return 1;
  }
  
  catch(const char *e)
  {
    output_verilog.error() << e << eom;
    return 1;
  }
  
  catch(int)
  {
    output_verilog.error();
    return 1;
  }

  return 0;
}

/*******************************************************************\

Function: show_transt::show_trans_verilog_rtl

  Inputs:

 Outputs:

 Purpose:

\*******************************************************************/

int show_transt::show_trans_verilog_rtl(std::ostream &out)
{
  output_verilog_rtlt output_verilog(
    symbol_table, out, get_message_handler());

  try
  {
    verilog_header(out, "Verilog RTL");
    output_verilog(*main_symbol);
  }
  
  catch(const std::string &e)
  {
    output_verilog.error() << e << eom;
    return 1;
  }
  
  catch(const char *e)
  {
    output_verilog.error() << e << eom;
    return 1;
  }
  
  catch(int)
  {
    output_verilog.error();
    return 1;
  }

  return 0;
}

/*******************************************************************\

Function: show_transt::verilog_header

  Inputs:

 Outputs:

 Purpose:

\*******************************************************************/

void show_transt::verilog_header(
  std::ostream &out,
  const std::string &desc)
{
  out << "// " << desc << " generated by EBMC Version "
      << EBMC_VERSION << '\n';
}

/*******************************************************************\

Function: show_transt::print_verilog_constraints

  Inputs:

 Outputs:

 Purpose:

\*******************************************************************/

void show_transt::print_verilog_constraints(
  const exprt &expr,
  std::ostream &out)
{
  if(expr.id()==ID_and)
  {
    forall_operands(it, expr)
      print_verilog_constraints(*it, out);
    return;
  }

  out << "  " << expr2verilog(expr) << '\n';

  out << '\n';
}

/*******************************************************************\

Function: show_transt::show_trans

  Inputs:

 Outputs:

 Purpose:

\*******************************************************************/

int show_transt::show_trans()
{
  int result=get_model();
  if(result!=-1) return result;

  std::cout << "Initial state constraints:\n\n";
  
  print_verilog_constraints(trans_expr.init(), std::cout);

  std::cout << "State constraints:\n\n";
  
  print_verilog_constraints(trans_expr.invar(), std::cout);

  std::cout << "Transition constraints:\n\n";
  
  print_verilog_constraints(trans_expr.trans(), std::cout);

  return 0;
}

/*******************************************************************\

Function: show_transt::show_trans_verilog_rtl

  Inputs:

 Outputs:

 Purpose:

\*******************************************************************/

int show_transt::show_trans_verilog_rtl()
{
  int result=get_model();
  if(result!=-1) return result;

  if(cmdline.isset("outfile"))
  {
    const std::string filename=cmdline.get_value("outfile");
    std::ofstream out(filename.c_str());
  
    if(!out)
    {
      std::cerr << "Failed to open `"
                << filename
                << "'" << '\n';
      return 1;
    }

    show_trans_verilog_rtl(out);
  }
  else
    show_trans_verilog_rtl(std::cout);

  return 0;
}

/*******************************************************************\

Function: show_transt::show_trans_verilog_netlist

  Inputs:

 Outputs:

 Purpose:

\*******************************************************************/

int show_transt::show_trans_verilog_netlist()
{
  int result=get_model();
  if(result!=-1) return result;

  if(cmdline.isset("outfile"))
  {
    const std::string filename=cmdline.get_value("outfile");
    std::ofstream out(filename.c_str());
  
    if(!out)
    {
      std::cerr << "Failed to open `"
                << filename
                << "'" << '\n';
      return 1;
    }

    show_trans_verilog_netlist(out);
  }
  else
    show_trans_verilog_netlist(std::cout);

  return 0;
}

/*******************************************************************\

Function: show_trans

  Inputs:

 Outputs:

 Purpose:

\*******************************************************************/

int show_trans(
  const cmdlinet &cmdline,
  ui_message_handlert &ui_message_handler)
{
  show_transt show_trans(cmdline, ui_message_handler);
  return show_trans.show_trans();
}

