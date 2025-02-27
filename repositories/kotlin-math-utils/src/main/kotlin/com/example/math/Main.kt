package com.example.math

/**
 * アプリケーションのエントリーポイント
 */
fun main() {
    println("数学ユーティリティライブラリへようこそ！")

    val calculator = Calculator()
    println("計算例: 5 + 3 = ${calculator.add(5, 3)}")
    println("計算例: 10 - 4 = ${calculator.subtract(10, 4)}")
    println("計算例: 6 * 7 = ${calculator.multiply(6, 7)}")
    println("計算例: 20 / 5 = ${calculator.divide(20, 5)}")

    println("\n高度な計算:")
    println("5の階乗 = ${calculator.factorial(5)}")
    println("17は素数か？ ${calculator.isPrime(17)}")
    println("10から20までの素数: ${calculator.getPrimes(10, 20)}")
    println("24と36の最大公約数: ${calculator.gcd(24, 36)}")
    println("24と36の最小公倍数: ${calculator.lcm(24, 36)}")

    println("\n数学ユーティリティ:")
    println("16の平方根: ${MathUtils.sqrt(16.0)}")
    println("-10の絶対値: ${MathUtils.abs(-10)}")
    println("2の8乗: ${MathUtils.power(2.0, 8)}")
    println("10のフィボナッチ数: ${MathUtils.fibonacci(10)}")

    println("\n統計計算:")
    val statisticsCalculator = StatisticsCalculator(calculator)
    val numbers = listOf(4, 7, 2, 9, 3, 5, 8, 1, 6)
    println("データ: $numbers")
    println("平均値: ${statisticsCalculator.mean(numbers)}")
    println("中央値: ${statisticsCalculator.median(numbers)}")
    println("最頻値: ${statisticsCalculator.mode(numbers)}")
    println("分散: ${statisticsCalculator.variance(numbers)}")
    println("標準偏差: ${statisticsCalculator.standardDeviation(numbers)}")
    println("範囲: ${statisticsCalculator.range(numbers)}")
} 
