#include <iostream>
#include <map>

struct OpDef{
	std::string op_name;
	float v_lhs;
	float v_rhs;
};

void chisla(int y, int x,
		std::map<float, int> v2c,
		std::map<float, OpDef> v2o,
		Dict& v2c,
		Dict& v2o,
