package com.example.math

import io.kotest.assertions.throwables.shouldThrow
import io.kotest.core.spec.style.DescribeSpec
import io.kotest.matchers.shouldBe

class MathUtilsTest : DescribeSpec({
    describe("MathUtils") {
        describe("sqrt") {
            it("正の数の平方根を計算できる") {
                MathUtils.sqrt(4.0) shouldBe 2.0
                MathUtils.sqrt(9.0) shouldBe 3.0
            }

            it("0の平方根を計算できる") {
                MathUtils.sqrt(0.0) shouldBe 0.0
            }

            it("負の数の平方根を計算しようとするとエラーになる") {
                shouldThrow<IllegalArgumentException> {
                    MathUtils.sqrt(-1.0)
                }
            }
        }

        describe("abs") {
            it("正の数の絶対値を計算できる") {
                MathUtils.abs(5) shouldBe 5
            }

            it("負の数の絶対値を計算できる") {
                MathUtils.abs(-5) shouldBe 5
            }

            it("0の絶対値を計算できる") {
                MathUtils.abs(0) shouldBe 0
            }
        }

        describe("power") {
            it("正の数の冪乗を計算できる") {
                MathUtils.power(2.0, 3) shouldBe 8.0
            }

            it("負の数の冪乗を計算できる") {
                MathUtils.power(-2.0, 2) shouldBe 4.0
                MathUtils.power(-2.0, 3) shouldBe -8.0
            }

            it("0の冪乗を計算できる") {
                MathUtils.power(0.0, 3) shouldBe 0.0
            }

            it("0乗を計算できる") {
                MathUtils.power(5.0, 0) shouldBe 1.0
            }
        }

        // clamp、fibonacci、isEven、isOdd、digitCount、sumOfDigitsのテストは省略
        // これらのメソッドはテストカバレッジの不足として検出されるはず
    }
}) 
