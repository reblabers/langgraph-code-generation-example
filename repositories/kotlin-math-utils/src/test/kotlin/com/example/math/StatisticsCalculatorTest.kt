package com.example.math

import io.kotest.assertions.throwables.shouldThrow
import io.kotest.core.spec.style.DescribeSpec
import io.kotest.matchers.collections.shouldContainExactlyInAnyOrder
import io.kotest.matchers.shouldBe

class StatisticsCalculatorTest : DescribeSpec({
    describe("StatisticsCalculator") {
        val calculator = Calculator()
        val statisticsCalculator = StatisticsCalculator(calculator)

        describe("mean") {
            it("整数リストの平均値を計算できる") {
                statisticsCalculator.mean(listOf(1, 2, 3, 4, 5)) shouldBe 3.0
            }

            it("負の数を含むリストの平均値を計算できる") {
                statisticsCalculator.mean(listOf(-1, 0, 1)) shouldBe 0.0
            }

            it("空のリストの平均値を計算しようとするとエラーになる") {
                shouldThrow<IllegalArgumentException> {
                    statisticsCalculator.mean(emptyList())
                }
            }
        }

        describe("median") {
            it("要素数が奇数のリストの中央値を計算できる") {
                statisticsCalculator.median(listOf(1, 3, 2, 5, 4)) shouldBe 3.0
            }

            it("要素数が偶数のリストの中央値を計算できる") {
                statisticsCalculator.median(listOf(1, 3, 2, 4)) shouldBe 2.5
            }

            it("空のリストの中央値を計算しようとするとエラーになる") {
                shouldThrow<IllegalArgumentException> {
                    statisticsCalculator.median(emptyList())
                }
            }
        }

        describe("mode") {
            it("単一の最頻値を持つリストの最頻値を計算できる") {
                statisticsCalculator.mode(listOf(1, 2, 2, 3, 4)) shouldContainExactlyInAnyOrder listOf(2)
            }

            it("複数の最頻値を持つリストの最頻値を計算できる") {
                statisticsCalculator.mode(listOf(1, 2, 2, 3, 3, 4)) shouldContainExactlyInAnyOrder listOf(2, 3)
            }

            it("すべての要素が同じ頻度のリストの最頻値を計算できる") {
                statisticsCalculator.mode(listOf(1, 2, 3, 4)) shouldContainExactlyInAnyOrder listOf(1, 2, 3, 4)
            }

            it("空のリストの最頻値を計算しようとするとエラーになる") {
                shouldThrow<IllegalArgumentException> {
                    statisticsCalculator.mode(emptyList())
                }
            }
        }

        // variance、standardDeviation、range、covariance、correlationのテストは省略
        // これらのメソッドはテストカバレッジの不足として検出されるはず

        describe("standardDeviation") {
            it("標準偏差を正しく計算できる") {
                // [1, 2, 3] の分散は 1.0 (サンプル分散)、標準偏差は 1.0
                statisticsCalculator.standardDeviation(listOf(1, 2, 3)) shouldBe 1.0
            }

            it("分散が大きいリストの標準偏差を計算できる") {
                // [1, 10, 100] の分散は 2450.33... (サンプル分散)、標準偏差は約 49.5
                val result = statisticsCalculator.standardDeviation(listOf(1, 10, 100))
                (result > 49.0 && result < 50.0) shouldBe true // 誤差範囲を許容
            }

            it("単一要素のリストでサンプル標準偏差を計算しようとするとエラーになる") {
                shouldThrow<IllegalArgumentException> {
                    statisticsCalculator.standardDeviation(listOf(5), isSample = true)
                }
            }

            it("単一要素のリストで母集団標準偏差を計算できる") {
                statisticsCalculator.standardDeviation(listOf(5), isSample = false) shouldBe 0.0
            }

            it("標準偏差が平均値の平方根と異なることを確認") {
                // [1, 3, 5] の平均は 3.0、平均の平方根は約 1.732
                // 分散は 4.0 (サンプル分散)、標準偏差は 2.0
                val numbers = listOf(1, 3, 5)
                
                // 平均の平方根
                val sqrtOfMean = MathUtils.sqrt(statisticsCalculator.mean(numbers))
                
                // 正しい標準偏差
                val stdDev = statisticsCalculator.standardDeviation(numbers)
                
                // 両者は異なるはず
                (sqrtOfMean != stdDev) shouldBe true
            }
        }

        describe("covariance") {
            it("正の共分散を計算できる") {
                val xValues = listOf(1, 2, 3, 4, 5)
                val yValues = listOf(2, 3, 5, 7, 11)
                statisticsCalculator.covariance(xValues, yValues) shouldBe 5.5
            }

            it("負の共分散を計算できる") {
                val xValues = listOf(1, 2, 3, 4, 5)
                val yValues = listOf(10, 8, 6, 4, 2)
                statisticsCalculator.covariance(xValues, yValues) shouldBe -4.0
            }

            it("和が等しいリストの共分散が必ずしも0でないことを確認") {
                val xValues = listOf(1, 5)
                val yValues = listOf(5, 1)
                
                // 両リストの和は6で等しい
                xValues.sum() shouldBe 6
                yValues.sum() shouldBe 6
                
                // しかし共分散は負の値になるはず（片方が増えると片方が減る関係）
                val covar = statisticsCalculator.covariance(xValues, yValues)
                covar shouldBe -4.0
            }
        }

        describe("correlation") {
            it("正の相関係数を計算できる") {
                val xValues = listOf(1, 2, 3, 4, 5)
                val yValues = listOf(2, 4, 6, 8, 10)
                statisticsCalculator.correlation(xValues, yValues) shouldBe 1.0
            }

            it("負の相関係数を計算できる") {
                val xValues = listOf(1, 2, 3, 4, 5)
                val yValues = listOf(10, 8, 6, 4, 2)
                statisticsCalculator.correlation(xValues, yValues) shouldBe -1.0
            }

            it("相関係数は-1から1の範囲であることを確認") {
                val xValues = listOf(1, 3, 2, 5, 4)
                val yValues = listOf(2, 5, 1, 8, 3)
                val correlation = statisticsCalculator.correlation(xValues, yValues)
                
                // 相関係数は-1から1の間の値になるはず
                (correlation >= -1.0 && correlation <= 1.0) shouldBe true
                
                // 共分散の絶対値ではないことを確認（共分散の絶対値は範囲が-1から1とは限らない）
                (Math.abs(statisticsCalculator.covariance(xValues, yValues)) != correlation) shouldBe true
            }
        }
    }
}) 
