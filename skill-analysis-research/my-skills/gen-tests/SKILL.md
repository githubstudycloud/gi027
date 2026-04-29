---
name: gen-tests
description: 测试生成助手 - 为已有代码补全测试，覆盖单元/集成/E2E各层。当用户说"生成测试"、"补充测试"、"写测试"、"test"时自动激活。
argument-hint: "[文件路径 或 类/模块名]"
allowed-tools: Read, Write, Glob, Grep, Bash
---

# 测试生成助手

为已有代码自动生成完整测试套件，遵循测试金字塔原则。

## 参数
- `$ARGUMENTS`：要为其生成测试的文件路径或模块名

## 工作流程

### 第一步：分析被测代码

读取 `$ARGUMENTS` 指定的文件，提取：
- 所有公共方法/函数
- 方法的输入参数类型和校验规则
- 可能的业务异常
- 外部依赖（DB、缓存、外部 API）

同时检查已有测试：
```bash
# 找对应的测试文件
find . -name "*Test*" -o -name "*.test.*" -o -name "*.spec.*" | grep -i "{module}"
```

### 第二步：确定测试层次

```
ServiceClass → 单元测试（Mock 所有外部依赖）
Controller/Router → 切片测试（@WebMvcTest / httpx AsyncClient）
Repository → 数据层测试（Testcontainers 真实 DB）
关键流程 → 集成测试（端到端，真实容器）
```

### 第三步：生成测试用例矩阵

对每个方法，生成以下维度的测试：

| 测试类型 | 描述 | 方法命名 |
|---------|------|---------|
| Happy Path | 正常输入，期望输出 | `should_{动词}_{结果}` |
| 边界值 | 最小值、最大值、空值 | `should_handle_{边界}_input` |
| 异常场景 | 资源不存在、权限不足 | `should_throw_{异常}_when_{条件}` |
| 并发场景 | 重复提交、并发修改 | `should_handle_concurrent_{操作}` |

### 第四步：生成测试代码

**Java - JUnit 5 + Mockito 单元测试：**

```java
@ExtendWith(MockitoExtension.class)
class {ClassName}Test {

    @Mock private {Dependency}Repository {dependency}Repository;
    @InjectMocks private {ClassName} {instance};

    // =========== Happy Path ===========

    @Test
    @DisplayName("正常创建{资源}时应返回完整{资源}信息")
    void should_create_{resource}_successfully() {
        // Given
        var request = {Builder}.validRequest().build();
        var saved = {Builder}.validEntity().id(1L).build();
        when({dependency}Repository.save(any())).thenReturn(saved);

        // When
        var result = {instance}.create(request);

        // Then
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getEmail()).isEqualTo(request.getEmail());
        verify({dependency}Repository, times(1)).save(any());
    }

    // =========== 异常场景 ===========

    @Test
    @DisplayName("{资源}不存在时应抛出 EntityNotFoundException")
    void should_throw_not_found_when_{resource}_not_exist() {
        // Given
        when({dependency}Repository.findById(99L)).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> {instance}.findById(99L))
            .isInstanceOf(EntityNotFoundException.class)
            .hasMessageContaining("99");
    }

    // =========== 边界场景 ===========

    @ParameterizedTest
    @NullAndEmptySource
    @DisplayName("无效输入应抛出校验异常")
    void should_throw_validation_when_input_invalid(String invalidInput) {
        assertThatThrownBy(() -> {instance}.create(new Request(invalidInput)))
            .isInstanceOf(ConstraintViolationException.class);
    }
}
```

**Python - pytest + AsyncMock：**

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.{module}.service import {ClassName}

class TestCreate{Resource}:
    """测试创建{资源}"""

    @pytest.fixture
    def service(self):
        mock_repo = AsyncMock()
        return {ClassName}(repo=mock_repo)

    @pytest.mark.asyncio
    async def test_create_success(self, service):
        """正常创建{资源}"""
        service.repo.save.return_value = MagicMock(id=1, email="test@test.com")

        result = await service.create(email="test@test.com", name="Test")

        assert result.id == 1
        service.repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_raises_when_email_duplicate(self, service):
        """邮箱重复时抛出异常"""
        from src.{module}.exceptions import DuplicateEmailException
        service.repo.find_by_email.return_value = MagicMock()

        with pytest.raises(DuplicateEmailException):
            await service.create(email="existing@test.com", name="Test")
```

**Vue - Vitest 组件测试：**

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import {ComponentName} from '@/components/{ComponentName}.vue'

describe('{ComponentName}', () => {
  const defaultProps = { /* 最小有效 props */ }

  beforeEach(() => setActivePinia(createPinia()))

  it('renders correctly with valid props', () => {
    const wrapper = mount({ComponentName}, { props: defaultProps })
    expect(wrapper.find('[data-test="{key-element}"]').exists()).toBe(true)
  })

  it('emits {event} when {action}', async () => {
    const wrapper = mount({ComponentName}, { props: defaultProps })
    await wrapper.find('[data-test="{trigger}"]').trigger('click')
    expect(wrapper.emitted('{event}')).toHaveLength(1)
  })

  it('shows error state when {condition}', () => {
    const wrapper = mount({ComponentName}, {
      props: { ...defaultProps, error: 'Something went wrong' }
    })
    expect(wrapper.find('[data-test="error-message"]').text())
      .toBe('Something went wrong')
  })
})
```

**Testcontainers 集成测试：**

```java
@SpringBootTest
@Testcontainers
@Transactional
class {Feature}IntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:16");

    @DynamicPropertySource
    static void props(DynamicPropertyRegistry r) {
        r.add("spring.datasource.url", postgres::getJdbcUrl);
        r.add("spring.datasource.username", postgres::getUsername);
        r.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired TestRestTemplate rest;

    @Test
    void full_{feature}_flow() {
        // 端到端测试关键业务流程
    }
}
```

### 第五步：输出覆盖率分析

```
生成的测试文件：
  ✅ {ClassName}Test.java（单元测试，{N} 个用例）
  ✅ {ClassName}IntegrationTest.java（集成测试，{N} 个用例）

预估覆盖率提升：
  当前：~{N}%
  生成后：~{N}%

未覆盖的场景（建议手动补充）：
  - {复杂业务逻辑，需要业务背景}
```
