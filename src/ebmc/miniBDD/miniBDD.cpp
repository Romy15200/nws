#include <cassert>

#include <iostream>

#include "miniBDD.h"

#define forall_nodes(it) for(nodest::const_iterator it=nodes.begin(); \
  it!=nodes.end(); it++)

namespace miniBDD
{

void node::remove_reference()
{
  assert(reference_counter!=0);
  
  reference_counter--;

  if(reference_counter==0 && node_number>=2)
  {
    mgr::reverse_keyt reverse_key(var, low, high);
    mgr->reverse_map.erase(reverse_key);
    low.clear();
    high.clear();
    mgr->free.push(this);
  } 
}

BDD mgr::Var(const std::string &label)
{
  var_table.push_back(var_table_entryt(label));
  true_bdd.node->var=var_table.size()+1;
  false_bdd.node->var=var_table.size()+1;
  return mk(var_table.size(), false_bdd, true_bdd);
}

void mgr::DumpDot(std::ostream &out, bool suppress_zero) const
{
  out << "digraph BDD {\n";

  out << "center = true;\n";
  
  out << "{ rank = same; { node [style=invis]; \"T\" };\n";
  
  if(!suppress_zero)
    out << "  { node [shape=box,fontsize=24]; \"0\"; }\n";
    
  out << "  { node [shape=box,fontsize=24]; \"1\"; }\n"
      << "}\n\n";
      
  for(unsigned v=0; v<var_table.size(); v++)
  {
    out << "{ rank=same; "
           "{ node [shape=plaintext,fontname=\"Times Italic\",fontsize=24] \" "
        << var_table[v].label
        << " \" }; ";

    forall_nodes(u)
      if(u->var==(v+1) && u->reference_counter!=0)
        out << '"' << u->node_number << "\"; ";
    
    out << "}\n";
  }

  out << '\n';

  out << "{ edge [style = invis];";

  for(unsigned v=0; v<var_table.size(); v++)
    out << " \" " << var_table[v].label
        << " \" ->";
  
  out << " \"T\"; }\n";
  
  out << '\n';

  forall_nodes(u)
  {
    if(u->reference_counter==0) continue;
    if(u->node_number<=1) continue;

    if(!suppress_zero || u->high.node_number()!=0)
      out << '"' << u->node_number << '"' << " -> "
          << '"' << u->high.node_number() << '"'
          << " [style=solid,arrowsize=\".75\"];\n";
        
    if(!suppress_zero || u->low.node_number()!=0)
      out << '"' << u->node_number << '"' << " -> "
          << '"' << u->low.node_number() << '"'
          << " [style=dashed,arrowsize=\".75\"];\n";

    out << '\n';
  }
  
  out << "}\n";
}

void mgr::DumpTikZ(
  std::ostream &out,
  bool suppress_zero,
  bool node_numbers) const
{
  out << "\\begin{tikzpicture}[node distance=1cm]\n";
  
  out << "  \\tikzstyle{BDDnode}=[circle,draw=black,"
         "inner sep=0pt,minimum size=5mm]\n";

  for(unsigned v=0; v<var_table.size(); v++)
  {
    out << "  \\node[";

    if(v!=0)
      out << "below of=v" << var_table[v-1].label;

    out << "] (v" << var_table[v].label << ") {$\\mathit{"
        << var_table[v].label << "}$};\n";

    unsigned previous=0;

    forall_nodes(u)
    {
      if(u->var==(v+1) && u->reference_counter!=0)
      {
        out << "  \\node[xshift=0cm, BDDnode, ";

        if(previous==0)
          out << "right of=v" << var_table[v].label;
        else
          out << "right of=n" << previous;

        out << "] (n" << u->node_number << ") {";
        if(node_numbers) out << "\\small $" << u->node_number << "$";
        out << "};\n";
        previous=u->node_number;
      }
    }
    
    out << '\n';
  }

  out << '\n';

  out << "  % terminals\n";
  out << "  \\node[draw=black, style=rectangle, below of=v"
      << var_table.back().label
      << ", xshift=1cm] (n1) {$1$};\n";
    
  if(!suppress_zero)
    out << "  \\node[draw=black, style=rectangle, left of=n1] (n0) {$0$};\n";

  out << '\n';

  out << "  % edges\n";
  out << '\n';

  forall_nodes(u)
  {
    if(u->reference_counter!=0 && u->node_number>=2)
    {
      if(!suppress_zero || u->low.node_number()!=0)
        out << "  \\draw[->,dashed] (n" << u->node_number << ") -> (n"
            << u->low.node_number() << ");\n";
          
      if(!suppress_zero || u->high.node_number()!=0)
        out << "  \\draw[->] (n" << u->node_number << ") -> (n"
            << u->high.node_number() << ");\n";
    }
  }

  out << '\n';
  
  out << "\\end{tikzpicture}\n";
}

bool equal_fkt(bool x, bool y)
{
  return x==y;
}

BDD BDD::operator ==(const BDD &other) const
{
  return apply(equal_fkt, *this, other);
}

bool xor_fkt(bool x, bool y)
{
  return x ^ y;
}

BDD BDD::operator ^(const BDD &other) const
{
  return apply(xor_fkt, *this, other);
}

BDD BDD::operator !() const
{
  return node->mgr->True() ^ *this;
}

bool and_fkt(bool x, bool y)
{
  return x && y;
}

BDD BDD::operator &(const BDD &other) const
{
  return apply(and_fkt, *this, other);
}

bool or_fkt(bool x, bool y)
{
  return x || y;
}

BDD BDD::operator |(const BDD &other) const
{
  return apply(or_fkt, *this, other);
}

mgr::mgr()
{
  // add true/false nodes
  nodes.push_back(node(this, 0, 0, BDD(), BDD()));
  false_bdd=BDD(&nodes.back());
  nodes.push_back(node(this, 1, 1, BDD(), BDD()));
  true_bdd=BDD(&nodes.back());
}

mgr::~mgr()
{
}

BDD mgr::mk(unsigned var, const BDD &low, const BDD &high)
{
  assert(var<=var_table.size());

  if(low.node_number()==high.node_number())
    return low;
  else
  {
    reverse_keyt reverse_key(var, low, high);
    reverse_mapt::const_iterator it=reverse_map.find(reverse_key);

    if(it!=reverse_map.end())
      return BDD(it->second);
    else
    {
      node *n;

      if(free.empty())
      {
        unsigned new_number=nodes.back().node_number+1;
        nodes.push_back(node(this, var, new_number, low, high));
        n=&nodes.back();
      }
      else // reuse a node
      {
        n=free.top();
        free.pop();
        n->var=var;
        n->low=low;
        n->high=high;
      }
      
      reverse_map[reverse_key]=n;
      return BDD(n);
    }
  }
}

bool operator < (const mgr::reverse_keyt &x,
                 const mgr::reverse_keyt &y)
{
  if(x.var<y.var) return true;
  if(x.var>y.var) return false;
  if(x.low<y.low) return true;
  if(x.low>y.low) return false;
  return x.high<y.high;
}

void mgr::DumpTable(std::ostream &out) const
{
  out << "\\# & \\mathit{var} & \\mathit{low} &"
         " \\mathit{high} \\\\\\hline\n";

  forall_nodes(it)
  {
    out << it->node_number << " & ";

    if(it->node_number==0 || it->node_number==1)
      out << it->var << " & & \\\\";
    else if(it->reference_counter==0)
      out << "- & - & - \\\\";
    else
      out << it->var << "\\," << var_table[it->var-1].label << " & "
          << it->low.node_number() << " & " << it->high.node_number()
          << " \\\\";
          
    if(it->node_number==1) out << "\\hline";

    out << " % " << it->reference_counter << '\n';
  }
}

BDD apply(bool (*fkt)(bool x, bool y), const BDD &x, const BDD &y)
{
  assert(x.node!=NULL && y.node!=NULL);
  assert(x.node->mgr==y.node->mgr);

  mgr *mgr=x.node->mgr;
  
  BDD u;

  if(x.is_constant() && y.is_constant())
    u=BDD(fkt(x.is_true(), y.is_true())?mgr->True():mgr->False());
  else if(x.var()==y.var())
    u=mgr->mk(x.var(),
              apply(fkt, x.low(), y.low()),
              apply(fkt, x.high(), y.high()));
  else if(x.var()<y.var())
    u=mgr->mk(x.var(),
              apply(fkt, x.low(), y),
              apply(fkt, x.high(), y));
  else /* x.var() > y.var() */
    u=mgr->mk(y.var(),
              apply(fkt, x, y.low()),
              apply(fkt, x, y.high()));
    
  return u;
}

BDD restrict(const BDD &u, const unsigned var, const bool value)
{
  // replace 'var' in 'u' by constant 'value'

  assert(u.node!=NULL);
  mgr *mgr=u.node->mgr;

  if(u.var()>var)
    return u;
  else if(u.var()<var)
    return mgr->mk(u.var(),
                   restrict(u.low(), var, value),
                   restrict(u.high(), var, value));
  else // u.var()==var
    return restrict(value?u.high():u.low(), var, value);
}

BDD exists(const BDD &u, const unsigned var)
{
  // u[var/0] OR u[var/1]
  return restrict(u, var, false) |
         restrict(u, var, true);
}

BDD substitute(const BDD &t, unsigned var, const BDD &tp)
{
  // t[var/tp] =
  //  ( tp & t[var/1]) |
  //  (!tp & t[var/0])

  return ( tp & restrict(t, var, true)) |
         (!tp & restrict(t, var, false));
}

} // namespace miniBDD
