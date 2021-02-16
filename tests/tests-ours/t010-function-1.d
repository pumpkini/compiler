
void say_hello(string s) {
  Print("hello " + s, "!");
}

int mul(int a, int b) {
  return a * b;
}

int main() {
  int a;
  int b;
  bool d;
  d = true;

  say_hello(ReadLine());

  a = 10;

  Print(xor(true, false));
  d = xor(true, d);
  Print(d);

  a = mul(ReadInteger(),ReadInteger());
  Print(a);

  Print(plusplus(-12.e2));
}

bool xor(bool a, bool b){
  bool c;
  c = a && !b || !a && b;
  return c;
}

double plusplus(double c)
{
  return c + 1.0;
}
