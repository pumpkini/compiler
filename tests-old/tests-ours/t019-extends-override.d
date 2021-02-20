
class A {
  public int val1;

  void f(double[][] a, int c) {
    Print("A");
  }
}

class B extends A{
  int val2;

  void print() {
    Print(val2, " ", val1);
  }

  void f(int[] a, int e) {
    Print("B");
  }
}

int main() {
    A a;
    B b;
    int[] i;
    double[] j;
    a = new A;
    b = new B;
    i = NewArray(1, int);
    j = NewArray(1, double);
    i[0] = 1;
    j[0] = 1.2;
    a.f(j, 3);
    a.val1 = 10;
    Print(a.val1);
    b.val1 = 12;
    b.val2 = 10;
    b.f(i, 1);
    b.print();
    a = b;
    a.f(j, 3);
    Print(a.val1);
}
