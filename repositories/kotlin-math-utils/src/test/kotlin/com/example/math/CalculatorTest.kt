package com.example.math

import io.kotest.assertions.throwables.shouldThrow
import io.kotest.core.spec.style.DescribeSpec
import io.kotest.matchers.shouldBe

class CalculatorTest : DescribeSpec({
    describe("Calculator") {
        val calculator = Calculator()

        describe("add") {
            it("正の数同士の加算ができる") {
                calculator.add(2, 3) shouldBe 5
            }

            it("負の数を含む加算ができる") {
                calculator.add(-2, 3) shouldBe 1
                calculator.add(2, -3) shouldBe -1
                calculator.add(-2, -3) shouldBe -5
            }
        }

        describe("subtract") {
            it("正の数同士の減算ができる") {
                calculator.subtract(5, 3) shouldBe 2
            }

            it("負の数を含む減算ができる") {
                calculator.subtract(-2, 3) shouldBe -5
                calculator.subtract(2, -3) shouldBe 5
                calculator.subtract(-2, -3) shouldBe 1
            }
        }

        describe("multiply") {
            it("正の数同士の乗算ができる") {
                calculator.multiply(2, 3) shouldBe 6
            }

            it("負の数を含む乗算ができる") {
                calculator.multiply(-2, 3) shouldBe -6
                calculator.multiply(2, -3) shouldBe -6
                calculator.multiply(-2, -3) shouldBe 6
            }

            it("0との乗算ができる") {
                calculator.multiply(0, 3) shouldBe 0
                calculator.multiply(2, 0) shouldBe 0
            }
        }

        describe("divide") {
            it("正の数同士の除算ができる") {
                calculator.divide(6, 3) shouldBe 2
            }

            it("負の数を含む除算ができる") {
                calculator.divide(-6, 3) shouldBe -2
                calculator.divide(6, -3) shouldBe -2
                calculator.divide(-6, -3) shouldBe 2
            }

            it("0で割ろうとするとエラーになる") {
                shouldThrow<IllegalArgumentException> {
                    calculator.divide(6, 0)
                }
            }
        }

        // factorial、isPrime、getPrimes、gcd、lcmのテストは省略
        // これらのメソッドはテストカバレッジの不足として検出されるはず
    }
}) 
