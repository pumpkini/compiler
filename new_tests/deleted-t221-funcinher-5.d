
class A {
}

class B extends A {
	void test() {
        Print("B.test()");
    }
}


int main() {
    A a;
    B b;
    b = new B;
    b.test();
    a = b;
    a.test();
}
