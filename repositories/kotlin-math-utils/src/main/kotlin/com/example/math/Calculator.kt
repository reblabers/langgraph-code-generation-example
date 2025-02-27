package com.example.math

/**
 * 様々な計算機能を提供する計算機クラス
 */
class Calculator {
    /**
     * 2つの数値を加算します
     *
     * @param a 1つ目の数値
     * @param b 2つ目の数値
     * @return 加算結果
     */
    fun add(
        a: Int,
        b: Int,
    ): Int {
        return a + b
    }

    /**
     * 2つの数値を減算します
     *
     * @param a 1つ目の数値
     * @param b 2つ目の数値
     * @return 減算結果
     */
    fun subtract(
        a: Int,
        b: Int,
    ): Int {
        return a - b
    }

    /**
     * 2つの数値を乗算します
     *
     * @param a 1つ目の数値
     * @param b 2つ目の数値
     * @return 乗算結果
     */
    fun multiply(
        a: Int,
        b: Int,
    ): Int {
        return a * b
    }

    /**
     * 2つの数値を除算します
     *
     * @param a 1つ目の数値
     * @param b 2つ目の数値
     * @return 除算結果
     * @throws IllegalArgumentException 0で除算しようとした場合
     */
    fun divide(
        a: Int,
        b: Int,
    ): Int {
        if (b == 0) {
            throw IllegalArgumentException("Cannot divide by zero")
        }
        return a / b
    }

    /**
     * 数値の階乗を計算します
     *
     * @param n 階乗を計算する数値
     * @return 階乗結果
     * @throws IllegalArgumentException 負の数を指定した場合
     */
    fun factorial(n: Int): Long {
        if (n < 0) {
            throw IllegalArgumentException("Factorial is not defined for negative numbers")
        }

        return when (n) {
            0, 1 -> 1
            else -> {
                var result = 1L
                for (i in 2..n) {
                    result *= i
                }
                result
            }
        }
    }

    /**
     * 数値が素数かどうかを判定します
     *
     * @param n 判定する数値
     * @return 素数の場合はtrue、そうでない場合はfalse
     */
    fun isPrime(n: Int): Boolean {
        if (n <= 1) return false
        if (n <= 3) return true
        if (n % 2 == 0 || n % 3 == 0) return false

        var i = 5
        while (i * i <= n) {
            if (n % i == 0 || n % (i + 2) == 0) return false
            i += 6
        }
        return true
    }

    /**
     * 指定された範囲内の素数を取得します
     *
     * @param start 範囲の開始値
     * @param end 範囲の終了値
     * @return 素数のリスト
     */
    fun getPrimes(
        start: Int,
        end: Int,
    ): List<Int> {
        return (start..end).filter { isPrime(it) }
    }

    /**
     * 2つの数値の最大公約数を計算します
     *
     * @param a 1つ目の数値
     * @param b 2つ目の数値
     * @return 最大公約数
     */
    fun gcd(
        a: Int,
        b: Int,
    ): Int {
        var x = a
        var y = b
        while (y != 0) {
            val temp = y
            y = x % y
            x = temp
        }
        return x
    }

    /**
     * 2つの数値の最小公倍数を計算します
     *
     * @param a 1つ目の数値
     * @param b 2つ目の数値
     * @return 最小公倍数
     */
    fun lcm(
        a: Int,
        b: Int,
    ): Int {
        return a / gcd(a, b) * b
    }
} 
