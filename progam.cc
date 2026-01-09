#include <iostream>
#include <fstream>
#include <omp.h>
#include <iomanip>
#include <string>

// Motor de elevamento usando __int128 para não estourar no cálculo modular
long long power(long long base, long long exp, long long mod) {
    long long res = 1;
    __int128 b = base % mod;
    while (exp > 0) {
        if (exp % 2 == 1) res = (long long)((__int128)res * b % mod);
        b = (b * b) % mod;
        exp /= 2;
    }
    return res;
}

bool e_primo_miller_rabin(long long num) {
    if (num < 2) return false;
    if (num == 2 || num == 3) return true;
    if (num % 2 == 0) return false;
    
    // PENEIRA RELÂMPAGO: Descarta múltiplos óbvios antes do teste pesado
    if (num % 3 == 0 || num % 5 == 0 || num % 7 == 0 || num % 11 == 0) return false;

    long long d = num - 1;
    int s = 0;
    while (d % 2 == 0) { d /= 2; s++; }
    
    static const long long bases[] = {2, 3, 7, 61}; // Bases suficientes para 64-bit
    for (long long a : bases) {
        if (num <= a) break;
        long long x = power(a, d, num);
        if (x == 1 || x == num - 1) continue; 
        bool composto = true;
        for (int r = 1; r < s; r++) {
            x = (long long)((__int128)x * x % num);
            if (x == num - 1) { composto = false; break; }
        }
        if (composto) return false;
    }
    return true;
}

int main() {
    long long n_atual = 146000000;

    std::ifstream leitura("checkpoint.txt");
    if (leitura.is_open()) {
        std::string buffer;
        // Pula o texto {"n_atual": para chegar no número
        std::getline(leitura, buffer, ':'); 
        leitura >> n_atual;
        leitura.close();
    }

    const int CHUNK_SIZE = 50000; 
    std::cout << "--- MISSAO LEGENDRE: MODO JSON TURBO ---" << std::endl;

    while (true) {
        bool falha_detectada = false;
        long long n_falha = -1;

        #pragma omp parallel for reduction(||:falha_detectada) lastprivate(n_falha) schedule(dynamic, 500)
        for (int i = 0; i < CHUNK_SIZE; i++) {
            if (falha_detectada) continue;
            
            long long n = n_atual + i;
            __int128 L_inf = (__int128)n * n;
            __int128 L_sup = (__int128)(n + 1) * (n + 1);
            bool achou_primo = false;
            
            long long inicio = (long long)((L_inf % 2 == 0) ? L_inf + 1 : L_inf + 2);

            for (long long j = inicio; j < (long long)L_sup; j += 2) {
                if (e_primo_miller_rabin(j)) {
                    achou_primo = true;
                    break;
                }
            }
            if (!achou_primo) {
                falha_detectada = true;
                n_falha = n;
            }
        }

        if (falha_detectada) {
            std::cout << "\n!!! FALHA NO N = " << n_falha << " !!!" << std::endl;
            break;
        }

        n_atual += CHUNK_SIZE;

        if (n_atual % 100000 == 0) {
            std::ofstream escrita("checkpoint.txt");
            // Salva exatamente no formato {"n_atual":146000000}
            escrita << "{\"n_atual\":" << n_atual << "}";
            escrita.close();
            
            std::cout << "Status: n = ";
            if (n_atual >= 10000000) {
                std::cout << std::scientific << std::setprecision(2) << (double)n_atual;
            } else {
                std::cout << std::fixed << n_atual;
            }
            std::cout << " | Salvo em JSON." << std::endl;
            std::cout << std::defaultfloat;
        }
    }
    return 0;
}