int factorial(int n)
{
  if (n <=1 ) return 1;
  return n*factorial(n-1);
}

void main()
{
   int n;
   for (n = 1; n <= 15; n = n + 1)
      Print("Factorial(", n , ") = ", factorial(n), "\n");
}