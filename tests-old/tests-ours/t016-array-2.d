
int main() {
    int[][][] a;
    int i;
    int j;
    int k;
    int c;

    c = 3;

    a = NewArray(c, int[][]);
   
    for (i = 0; i < c; i = i + 1)
    {
        a[i] = NewArray(2, int[]);
       for (j = 0; j < a[i].length(); j = j + 1)
        {
           //  Print("a[i][j].len?", i, " ", j);
         //   a[i][j] = NewArray(ReadInteger(), int);
            a[i][j] = NewArray(4, int);
             for (k = 0; k < a[i][j].length(); k = k + 1)
            {
                a[i][j][k] = i * 100 + j * 10 + k;
            }
        }
        
    }
   
    for (i = 0; i < c; i = i + 1)
    {
       for (j = 0; j < a[i].length(); j = j + 1)
        {
            Print("a[i][j].len: ", i, " ", j, " ", a[i][j].length());
            for(k = 0; k < a[i][j].length(); k = k + 1)
            {
                Print(a[i][j][k]);
            }
              Print("-");
        }
        
        Print("::::");
    }
   
}
