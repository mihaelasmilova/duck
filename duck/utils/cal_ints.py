import json,pickle,sys,os
from parmed.geometry import distance2
from parmed.topologyobjects import Atom
import operator
import parmed
import math
def check_same(atom,chain,res_name,res_number,atom_name):
  if atom.residue.name == res_name:
    if atom.residue.number == res_number:
      if atom.name == atom_name:
        if atom.residue.chain == chain:
          return True
  return False

def is_lig(atom):
  if atom.residue.name=="LIG" and atom.atomic_number in [7,8]:
    return True

def find_interaction(res_atom=None,prot_file=None):
  output_file = "indice.text"
  if not res_atom or prot_file:
    if os.path.isfile(output_file):
      return json.load(open(output_file))
  # Parse the input data like this -> "A_LYS_311_N"
  chain  = res_atom.split("_")[0]
  res_name = res_atom.split("_")[1]
  res_number = int(res_atom.split("_")[2])
  atom_name = res_atom.split("_")[3]
  # Read the original PDB File and find the atom coords
  print("loading system")
  protein=parmed.load_file(prot_file)
  for atom in protein.atoms:
    if check_same(atom,chain,res_name,res_number,atom_name):
      prot_atom = atom
      break
  # Read files
  print("loading pickle")
  pickle_in=open('complex_system.pickle', 'rb')
  combined_pmd = pickle.load(pickle_in)[0]
  pickle_in.close()
  distance_atom_1 = [(x.idx,distance2(x,prot_atom)) for x in combined_pmd.atoms]
  distance_atom_1.sort(key=operator.itemgetter(1))
  # Now find the one nearest
  atom = Atom()
  distance_atom_2 = [(x.idx,distance2(x,prot_atom)) for x in combined_pmd.atoms if is_lig(x)]
  distance_atom_2.sort(key=operator.itemgetter(1))
  # These are the interactions to find
  print(distance_atom_1[0])
  print(distance_atom_2[0])
  index_one = distance_atom_1[0][0]
  index_two = distance_atom_2[0][0]
  out_f = open(output_file,"w")
  out_f.write(json.dumps([index_one,index_two]))
  out_f.close()
  return [output_file,math.sqrt(distance_atom_2[0][1])]

if __name__ =="__main__":
  # Define the input
  res_atom = sys.argv[1]
  prot_file = sys.argv[2]
  find_interaction(res_atom,prot_file)