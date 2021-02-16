
int g;

class Test {
    void test() {
        Print(g);
    }
}

int main() {
    Test t;
    t = new Test;
    g = 1;
    t.test();
}
