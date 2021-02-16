int main() {
    double d1;
    double d2;
    int i1;
    int i2;
    bool b1;
    bool b2;

    double rd;
    int ri;

    d1 = 1.5741691;
    d2 = -0.1245714;

    i1 = ReadInteger();
    i2 = ReadInteger();
    ri = ri + (i1 % i2) * (i2 % i1);
    rd = rd + itod((i1 * i2) % (btoi(i1 == i2) * 2 + 2)) * itod(ri) * d1;

    i1 = ReadInteger();
    i2 = ReadInteger();
    ri = ri + (i1 % i2) * (i2 % i1);
    rd = rd + itod((i1 * i2) % (btoi(i1 == i2) * 2 + 2)) * itod(ri) * d2;

    i1 = ReadInteger();
    i2 = ReadInteger();
    ri = ri + (i1 % i2) * (i2 % i1);
    rd = rd + itod((i1 * i2) % (btoi(i1 == i2) * 2 + 2)) * itod(ri) * d1;

    i1 = ReadInteger();
    i2 = ReadInteger();
    ri = ri + (i1 % i2) * (i2 % i1);
    rd = rd + itod((i1 * i2) % (btoi(i1 == i2) * 2 + 2)) * itod(ri) * d2;

    i1 = ReadInteger();
    i2 = ReadInteger();
    ri = ri + (i1 % i2) * (i2 % i1);
    rd = rd + itod((i1 * i2) % (btoi(i1 == i2) * 2 + 2)) * itod(ri) * d1;

    i1 = ReadInteger();
    i2 = ReadInteger();
    ri = ri + (i1 % i2) * (i2 % i1);
    rd = rd + itod((i1 * i2) % (btoi(i1 == i2) * 2 + 2)) * itod(ri) * d2;

    Print(rd);

}
