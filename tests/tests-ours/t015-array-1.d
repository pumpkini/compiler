
int main() {
    int[] a;
    int[] b;
    int i;

    a = NewArray(4, int);
    b = a;
    for (i = 0; i < 4; i = i + 1)
    {
        a[i] = ReadInteger() * 10;
    }
    Print(a==b);
    Print(a==a);
    b = a + b + b;
    for (i = 0; i < b.length(); i = i + 1)
    {
        Print(b[i]);
    }
}
