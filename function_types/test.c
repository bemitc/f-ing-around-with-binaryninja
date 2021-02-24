#include <stdio.h>

int main(int argc, char** argv)
{
    int a;

    printf("%d %s\n", a, argv[0]);
    printf("%p\n", argv[0]);

    return 0;
}