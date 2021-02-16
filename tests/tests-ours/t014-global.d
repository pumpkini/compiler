

class person{
  string name;
  int age;
}
person p2;

void f() {
  Print(glob);
  glob = glob * glob;
}

int main() {
    glob = 4;
    f();
    Print(glob);
    Print(p2 == p);
    p = new person;
    Print(p2 == null);
    p.name = "saba";
    print_name(p);
}

int glob;
person p;


void print_name(person a) {
  Print(a.name);
}
