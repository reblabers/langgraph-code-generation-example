# Kotlin Math Utils

数学的な計算機能を提供するKotlinライブラリです。

## 機能

このライブラリは以下の機能を提供します：

### 基本計算機能 (Calculator)

- 加算、減算、乗算、除算
- 階乗計算
- 素数判定
- 素数リスト取得
- 最大公約数 (GCD)
- 最小公倍数 (LCM)

### 数学ユーティリティ (MathUtils)

- 平方根計算
- 絶対値計算
- 冪乗計算
- 範囲内クランプ
- フィボナッチ数列
- 偶数/奇数判定
- 桁数計算
- 各桁の合計計算

### 統計計算 (StatisticsCalculator)

- 平均値
- 中央値
- 最頻値
- 分散
- 標準偏差
- 範囲
- 共分散
- 相関係数

## 使用例

```kotlin
// 基本計算
val calculator = Calculator()
val sum = calculator.add(5, 3)  // 8
val product = calculator.multiply(4, 7)  // 28

// 数学ユーティリティ
val sqrt = MathUtils.sqrt(16.0)  // 4.0
val fibonacci = MathUtils.fibonacci(10)  // 55

// 統計計算
val statisticsCalculator = StatisticsCalculator(calculator)
val numbers = listOf(4, 7, 2, 9, 3, 5, 8, 1, 6)
val mean = statisticsCalculator.mean(numbers)  // 5.0
val median = statisticsCalculator.median(numbers)  // 5.0
```

## ビルド方法

```bash
./gradlew build
```

## テスト実行

```bash
./gradlew test
```

## ライセンス

MIT 