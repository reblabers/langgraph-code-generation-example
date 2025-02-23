from langchain_core.tools import tool
from typing import Annotated

@tool
def apply_diff(
    diff: Annotated[str, 'unified diff形式の文字列'],
) -> str:
    r"""
    受け取ったDIFFをコードに適用します。

    Diff Example:
    --- original.kt
    +++ mutated.kt
    @@ -180,10 +180,10 @@
        * @return 見つかったプロパティを [KtProperty] として返します。見つからない場合は null を返します。
        */
        fun findKtProperty(qualifiedPropertyName: String): KtProperty? {
    -        val targetFqName = FqName(qualifiedPropertyName)
    -        return findKtClass(targetFqName.parent().asString())?.let { ktClass ->
    +        val propertyName = qualifiedPropertyName.substringAfterLast(".")
    +        return findKtClass(qualifiedPropertyName.substringBeforeLast("."))?.let { ktClass ->
                val properties = ktClass.getProperties()
    -            return properties.firstOrNull { it.fqName == targetFqName }
    +            return properties.firstOrNull { it.name == propertyName }
            }
        }
    """
    return diff
