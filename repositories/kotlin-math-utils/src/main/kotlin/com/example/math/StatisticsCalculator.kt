package com.example.math

/**
 * 統計計算を行うクラス
 */
class StatisticsCalculator(private val calculator: Calculator) {
    /**
     * 数値リストの平均値を計算します
     *
     * @param numbers 数値リスト
     * @return 平均値
     * @throws IllegalArgumentException 空のリストを指定した場合
     */
    fun mean(numbers: List<Int>): Double {
        if (numbers.isEmpty()) {
            throw IllegalArgumentException("Cannot calculate mean of empty list")
        }

        val sum = numbers.sum()
        return sum.toDouble() / numbers.size
    }

    /**
     * 数値リストの中央値を計算します
     *
     * @param numbers 数値リスト
     * @return 中央値
     * @throws IllegalArgumentException 空のリストを指定した場合
     */
    fun median(numbers: List<Int>): Double {
        if (numbers.isEmpty()) {
            throw IllegalArgumentException("Cannot calculate median of empty list")
        }

        val sorted = numbers.sorted()
        val middle = sorted.size / 2

        return if (sorted.size % 2 == 0) {
            (sorted[middle - 1] + sorted[middle]) / 2.0
        } else {
            sorted[middle].toDouble()
        }
    }

    /**
     * 数値リストの最頻値を計算します
     *
     * @param numbers 数値リスト
     * @return 最頻値のリスト（同じ頻度の値が複数ある場合は複数返す）
     * @throws IllegalArgumentException 空のリストを指定した場合
     */
    fun mode(numbers: List<Int>): List<Int> {
        if (numbers.isEmpty()) {
            throw IllegalArgumentException("Cannot calculate mode of empty list")
        }

        val frequencyMap = numbers.groupingBy { it }.eachCount()
        val maxFrequency = frequencyMap.values.maxOrNull() ?: 0

        return frequencyMap.filter { it.value == maxFrequency }.keys.toList()
    }

    /**
     * 数値リストの分散を計算します
     *
     * @param numbers 数値リスト
     * @param isSample サンプル分散を計算するかどうか
     * @return 分散
     * @throws IllegalArgumentException 空のリスト、または要素が1つしかないリストでサンプル分散を計算しようとした場合
     */
    fun variance(
        numbers: List<Int>,
        isSample: Boolean = true,
    ): Double {
        if (numbers.isEmpty()) {
            throw IllegalArgumentException("Cannot calculate variance of empty list")
        }

        if (isSample && numbers.size == 1) {
            throw IllegalArgumentException("Cannot calculate sample variance with only one value")
        }

        val avg = mean(numbers)
        val sumOfSquaredDifferences = numbers.sumOf { MathUtils.power(it - avg, 2) }

        return if (isSample) {
            sumOfSquaredDifferences / (numbers.size - 1)
        } else {
            sumOfSquaredDifferences / numbers.size
        }
    }

    /**
     * 数値リストの標準偏差を計算します
     *
     * @param numbers 数値リスト
     * @param isSample サンプル標準偏差を計算するかどうか
     * @return 標準偏差
     * @throws IllegalArgumentException 空のリスト、または要素が1つしかないリストでサンプル標準偏差を計算しようとした場合
     */
    fun standardDeviation(
        numbers: List<Int>,
        isSample: Boolean = true,
    ): Double {
        return MathUtils.sqrt(variance(numbers, isSample))
    }

    /**
     * 数値リストの範囲を計算します
     *
     * @param numbers 数値リスト
     * @return 範囲（最大値 - 最小値）
     * @throws IllegalArgumentException 空のリストを指定した場合
     */
    fun range(numbers: List<Int>): Int {
        if (numbers.isEmpty()) {
            throw IllegalArgumentException("Cannot calculate range of empty list")
        }

        val min = numbers.minOrNull() ?: 0
        val max = numbers.maxOrNull() ?: 0

        return calculator.subtract(max, min)
    }

    /**
     * 2つの数値リスト間の共分散を計算します
     *
     * @param xValues 1つ目の数値リスト
     * @param yValues 2つ目の数値リスト
     * @param isSample サンプル共分散を計算するかどうか
     * @return 共分散
     * @throws IllegalArgumentException リストの長さが異なる場合、または空のリストを指定した場合
     */
    fun covariance(
        xValues: List<Int>,
        yValues: List<Int>,
        isSample: Boolean = true,
    ): Double {
        if (xValues.size != yValues.size) {
            throw IllegalArgumentException("Lists must have the same size")
        }

        if (xValues.isEmpty()) {
            throw IllegalArgumentException("Cannot calculate covariance of empty lists")
        }

        if (isSample && xValues.size == 1) {
            throw IllegalArgumentException("Cannot calculate sample covariance with only one pair of values")
        }

        val xMean = mean(xValues)
        val yMean = mean(yValues)

        val sumOfProducts = xValues.zip(yValues).sumOf { (x, y) -> (x - xMean) * (y - yMean) }

        return if (isSample) {
            sumOfProducts / (xValues.size - 1)
        } else {
            sumOfProducts / xValues.size
        }
    }

    /**
     * 2つの数値リスト間の相関係数を計算します
     *
     * @param xValues 1つ目の数値リスト
     * @param yValues 2つ目の数値リスト
     * @return 相関係数
     * @throws IllegalArgumentException リストの長さが異なる場合、または空のリストを指定した場合
     */
    fun correlation(
        xValues: List<Int>,
        yValues: List<Int>,
    ): Double {
        val cov = covariance(xValues, yValues)
        val stdDevX = standardDeviation(xValues)
        val stdDevY = standardDeviation(yValues)

        return cov / (stdDevX * stdDevY)
    }
} 
