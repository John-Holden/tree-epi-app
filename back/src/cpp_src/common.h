#include <string>
#include <iostream>
#include <fstream>
#include <jsoncpp/json/json.h>
#include <vector>

using namespace std; // use all std object names etc. 
using std :: vector;


// print a seq char
void PrintChar(string char_seq) {std:: cout << char_seq << std :: endl;}


// print a vector
void PrintVect (const vector<int>& v){
  //vector<int> v;
  for (int i=0; i<v.size();i++){
    cout << v[i] << endl;
  }
}


// load a json object
Json::Value LoadJson(string sim_loc)
{   
    ifstream parameter_input(sim_loc+"/parameters.json");
    Json::Reader reader;
    Json::Value root;
    reader.parse(parameter_input, root);
    return root;
}


// Load a csv item
vector<int> LoadField(string SimName)
{   
    int val;
    string line;
    vector<int> dataField;
    fstream CSVfile (SimName, ios::in);
    if(!CSVfile.is_open()) throw std::runtime_error("Error could not open file in " + SimName);
    if (CSVfile.good()) {} else {throw std::runtime_error("Error detected in file stream!");}
    
    while (getline(CSVfile, line)) 
    {
        int index = 0;
        std: stringstream ss(line);
        while(ss >> val)
            {   
                dataField.push_back(val);
                if(ss.peek() == ',') ss.ignore();
                index ++;
            }    
    }
    
    return dataField;
}


//ints - write vector v to text.txt
void writeFieldInt(vector<int> v, string saveName){
	ofstream file;
	file.open(saveName);
	for(int i=0;i<v.size();++i){
		file<<v[i]<<"\n";
	}  
	file.close();
}

// floats - write vector v to text.txt
void writeFieldFloat(vector<float> v, string saveName){
	ofstream file;
	file.open(saveName);
	for(int i=0;i<v.size();++i){
		file<<v[i]<<"\n";
	}  
	file.close();
}

// stupid func to signal end of sim
void writeEnd(string SimName) {
  ofstream file;
	file.open(SimName+"/end");
	file.close();
}

// Save in correct format
string frameLabel(int t) {
  if (t < 10) {
    return "000" + to_string(t);
  }
  else if (t < 100) {
    return "00" + to_string(t);
  }
  else if (t < 1000) {
    return "0" + to_string(t);
  }
  return to_string(t);
}