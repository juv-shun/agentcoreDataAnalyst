# Data Analyst Agent

AWS Bedrock AgentCore と Strands Agents を使用したデータ分析エージェント。
S3 上の CSV ファイルを自然言語で分析できます。

## アーキテクチャ

### 全体構成

```mermaid
graph LR
    subgraph web ["Webアプリ"]
        A[Backend]
    end

    subgraph aws ["AWS"]
        subgraph agentcore ["AWS Bedrock AgentCore"]
            subgraph runtime ["AgentCore Runtime"]
                C[Strands Agent]
            end
            D[Code Interpreter]
        end
        E[S3 Bucket]
        F[Bedrock Claude 4.5 Haiku]
    end

    A -->|invoke| C
    C -->|tool call| D
    D -->|download CSV| E
    C -->|inference| F

    style web fill:#e1f5fe,stroke:#01579b
    style aws fill:#fff3e0,stroke:#e65100
    style agentcore fill:#f3e5f5,stroke:#4a148c
    style runtime fill:#e8f5e9,stroke:#1b5e20
```

### 処理フロー

```mermaid
sequenceDiagram
    participant Client as Webバックエンド
    participant Agent as AgentCore Runtime<br/>(Strands)
    participant LLM
    participant CI as Code Interpreter
    participant S3

    Client->>Agent: プロンプト送信<br/>(S3パス + 分析リクエスト)

    loop 自律的な推論と実行 (Agentic Loop)
        Agent->>LLM: 思考: 次のステップを決定
        LLM-->>Agent: アクション: ツール実行 or 最終回答
        Agent-->>Client: ストリーミングレスポンス送信

        opt ツール実行が必要な場合
            Agent->>CI: Pythonコード実行
            CI->>S3: CSVファイル取得
            S3-->>CI: CSVデータ
            CI->>CI: pandas分析実行
            CI-->>Agent: 実行結果
        end
    end
```

## 前提条件

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/)（パッケージマネージャ）
- AWS CLI（認証設定済み）
- bedrock-agentcore-starter-toolkit

## 環境セットアップ

### 1. 依存関係のインストール:

```bash
uv sync
```

### 2. AWS インフラのデプロイ（CDK）

本 AI エージェントは、ツールとして、AWS Bedrock の Code Interpreter を使用します。
したがって、ローカル実行であっても、CDK を使って、AWS 環境をデプロイする必要があります。

```bash
uv run cdk bootstrap
uv run cdk deploy --all --require-approval never
```

これにより以下がデプロイされます:

- S3 バケット（データ保存用）
- Code Interpreter（Python コード実行環境）
  - 現在、SANDBOX 環境ではなぜか S3 へのアクセスができないため、ネットワークモードを PUBLIC にしている。
- AgentCore Runtime 用 IAM ロール（agentcore deploy で使用）

### 3. agentcore CLI の設定

```bash
export RUNTIME_ROLE_ARN=$(aws cloudformation describe-stacks \
  --stack-name DataAnalystRuntimeRoleStack \
  --query "Stacks[0].Outputs[?OutputKey=='AgentCoreRuntimeRoleArn'].OutputValue" \
  --output text --region ap-northeast-1)

agentcore configure -e src/main.py -er $RUNTIME_ROLE_ARN -r ap-northeast-1
```

設定値は、各自好きなように設定してください。サンプルを以下に示します。

- Agent name: 任意
- Path or Press Enter to use detected dependency file: pyproject.toml
- Deployment Configuration: Direct Code Deploy
- Select Python runtime version: PYTHON_3_13
- Execution Role: (empty)
- S3 Bucket: (empty)
- Authorization Configuration: (empty)
- Configure request header allowlist?: (empty)
- MemoryManager: (empty)
- Optional: Long-term memory: (empty)

## ローカルで動作確認

### 1. ローカルでエージェントを起動

```bash
export CODE_INTERPRETER_ID=$(aws cloudformation describe-stacks \
  --stack-name DataAnalystCodeInterpreterStack \
  --query "Stacks[0].Outputs[?OutputKey=='CodeInterpreterId'].OutputValue" \
  --output text --region ap-northeast-1)

agentcore dev --env CODE_INTERPRETER_ID=$CODE_INTERPRETER_ID
```

### 2. 動作確認

```bash
agentcore invoke --dev '{"prompt": "1+1は？"}'
```

なお、ペイロードは以下のフォーマットで渡す必要があります。
s3 キーは任意です。

```json
{
  "prompt": "1+1は？"
  "s3": "s3://..."
}
```

## AWS へのデプロイ&動作確認

### 1. AgentCore Runtime へのデプロイ

```bash
export CODE_INTERPRETER_ID=$(aws cloudformation describe-stacks \
  --stack-name DataAnalystCodeInterpreterStack \
  --query "Stacks[0].Outputs[?OutputKey=='CodeInterpreterId'].OutputValue" \
  --output text --region ap-northeast-1)

agentcore deploy --env CODE_INTERPRETER_ID=$CODE_INTERPRETER_ID
```

### 2. 動作確認

```bash
agentcore invoke '{"prompt": "1+1は？"}'
```

## プロジェクト構成

```
.
├── src/
│   ├── main.py                 # エージェント実装
│   └── system_prompt.md        # システムプロンプト
├── infra/                      # AWS CDK インフラ
│   ├── app.py
│   └── stacks/
│       ├── agentcore_runtime_role_stack.py
│       ├── code_interpreter_stack.py
│       └── storage_stack.py
├── .bedrock_agentcore.yaml     # agentcore 設定
├── cdk.json
└── pyproject.toml
```

本リポジトリは、ゼロから作るテンプレート的位置づけであるため、 `.bedrock_agentcore.yaml` は git 管理から除外されています。
