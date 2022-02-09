typedef unsigned char uchar;
typedef unsigned short ushort;
typedef unsigned long ulong;

uchar N = 16;

uchar multiplyBy02(uchar n)
{
    return (n << 1) ^ ((n >> 7) * 0x1B);
}

uchar multiplyBy03(uchar n)
{
    return multiplyBy02(n) ^ n;
}

uchar multiplyBy09(uchar n)
{
    return multiplyBy02(multiplyBy02(multiplyBy02(n))) ^ n;
}

uchar multiplyBy0B(uchar n)
{
    return multiplyBy02(multiplyBy02(multiplyBy02(n)) ^ n) ^ n;
}

uchar multiplyBy0D(uchar n)
{
    return multiplyBy02(multiplyBy02(multiplyBy02(n) ^ n)) ^ n;
}

uchar multiplyBy0E(uchar n)
{
    return multiplyBy02(multiplyBy02(multiplyBy02(n) ^ n) ^ n);
}

void mixColumns(uchar *state)
{
    uchar temp[N];
    for (uchar i = 0; i < N; i++)
    {
        temp[i] = state[i];
    }

    for (uchar i = 0; i < 4; i++)
    {
        state[i] = multiplyBy02(temp[i]) ^ multiplyBy03(temp[4 + i]) ^ temp[8 + i] ^ temp[12 + i];
        state[i + 4] = temp[i] ^ multiplyBy02(temp[4 + i]) ^ multiplyBy03(temp[8 + i]) ^ temp[12 + i];
        state[i + 8] = temp[i] ^ temp[4 + i] ^ multiplyBy02(temp[8 + i]) ^ multiplyBy03(temp[12 + i]);
        state[i + 12] = multiplyBy03(temp[i]) ^ temp[4 + i] ^ temp[8 + i] ^ multiplyBy02(temp[12 + i]);
    }
}

void invMixColumns(uchar *state)
{
    uchar temp[N];
    for (uchar i = 0; i < N; i++)
    {
        temp[i] = state[i];
    }

    for (uchar i = 0; i < 4; i++)
    {
        state[i] = multiplyBy0E(temp[i]) ^ multiplyBy0B(temp[4 + i]) ^ multiplyBy0D(temp[8 + i]) ^ multiplyBy09(temp[12 + i]);
        state[i + 4] = multiplyBy09(temp[i]) ^ multiplyBy0E(temp[4 + i]) ^ multiplyBy0B(temp[8 + i]) ^ multiplyBy0D(temp[12 + i]);
        state[i + 8] = multiplyBy0D(temp[i]) ^ multiplyBy09(temp[4 + i]) ^ multiplyBy0E(temp[8 + i]) ^ multiplyBy0B(temp[12 + i]);
        state[i + 12] = multiplyBy0B(temp[i]) ^ multiplyBy0D(temp[4 + i]) ^ multiplyBy09(temp[8 + i]) ^ multiplyBy0E(temp[12 + i]);
    }
}