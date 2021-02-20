
class A {
  public int val1;

  void f() {
    Print("A");
  }
}

class B extends A{
  int val2;
  int val1;

  void print() {
    Print(val2, " ", val1);
  }

  void f() {
    Print("B");
  }
}

int main() {
    A a;
    B b;
    a = new A;
    b = new B;
    a.f();
    a.val1 = 10;
    Print(a.val1);
    b.val1 = 12;
    b.val2 = 10;
    b.f();
    b.print();
    a = b;
    a.f();
    Print(a.val1);
}
