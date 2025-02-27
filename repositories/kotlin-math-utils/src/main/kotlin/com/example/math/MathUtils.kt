package com.example.math

/**
 * 数学的な操作を提供するユーティリティクラス
 */
object MathUtils {
    /**
     * 数値の平方根を計算します
     *
     * @param n 平方根を計算する数値
     * @return 平方根
     * @throws IllegalArgumentException 負の数を指定した場合
     */
    fun sqrt(n: Double): Double {
        if (n < 0) {
            throw IllegalArgumentException("Cannot calculate square root of negative number")
        }
        return Math.sqrt(n)
    }

    /**
     * 数値の絶対値を計算します
     *
     * @param n 絶対値を計算する数値
     * @return 絶対値
     */
    fun abs(n: Int): Int {
        return if (n < 0) -n else n
    }

    /**
     * 数値の冪乗を計算します
     *
     * @param base 底
     * @param exponent 指数
     * @return 冪乗結果
     */
    fun power(
        base: Double,
        exponent: Int,
    ): Double {
        return Math.pow(base, exponent.toDouble())
    }

    /**
     * 数値を指定された範囲内に収めます
     *
     * @param value 対象の数値
     * @param min 最小値
     * @param max 最大値
     * @return 範囲内に収められた数値
     */
    fun clamp(
        value: Int,
        min: Int,
        max: Int,
    ): Int {
        return when {
            value < min -> min
            value > max -> max
            else -> value
        }
    }

    /**
     * フィボナッチ数列のn番目の値を計算します
     *
     * @param n インデックス
     * @return フィボナッチ数列のn番目の値
     * @throws IllegalArgumentException 負の数を指定した場合
     */
    fun fibonacci(n: Int): Long {
        if (n < 0) {
            throw IllegalArgumentException("Fibonacci is not defined for negative indices")
        }

        if (n <= 1) return n.toLong()

        var a = 0L
        var b = 1L

        for (i in 2..n) {
            val temp = a + b
            a = b
            b = temp
        }

        return b
    }

    /**
     * 指定された数値が偶数かどうかを判定します
     *
     * @param n 判定する数値
     * @return 偶数の場合はtrue、奇数の場合はfalse
     */
    fun isEven(n: Int): Boolean {
        return n % 2 == 0
    }

    /**
     * 指定された数値が奇数かどうかを判定します
     *
     * @param n 判定する数値
     * @return 奇数の場合はtrue、偶数の場合はfalse
     */
    fun isOdd(n: Int): Boolean {
        return n % 2 != 0
    }

    /**
     * 指定された数値の桁数を計算します
     *
     * @param n 対象の数値
     * @return 桁数
     */
    fun digitCount(n: Int): Int {
        return n.toString().length
    }

    /**
     * 指定された数値の各桁の合計を計算します
     *
     * @param n 対象の数値
     * @return 各桁の合計
     */
    fun sumOfDigits(n: Int): Int {
        return n.toString().sumOf { it.toString().toInt() }
    }
} 
