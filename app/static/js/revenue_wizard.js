// ==========================================================
// 収益事業モデル診断ウィザード用のJavaScript
// ==========================================================

/**
 * ウィザードの状態管理
 */
class WizardState {
  constructor() {
    this.currentStep = 1;
    this.totalSteps = 5;
    this.answers = {};
  }

  /**
   * 次のステップに進む
   * @returns {boolean} 次のステップに進めたかどうか
   */
  nextStep() {
    if (this.currentStep < this.totalSteps) {
      this.currentStep++;
      this.updateUI();
      return true;
    }
    return false;
  }

  /**
   * 前のステップに戻る
   * @returns {boolean} 前のステップに戻れたかどうか
   */
  prevStep() {
    if (this.currentStep > 1) {
      this.currentStep--;
      this.updateUI();
      return true;
    }
    return false;
  }

  /**
   * UI要素の表示を更新
   */
  updateUI() {
    // ステップインジケーターの更新
    document.querySelectorAll(".step-indicator").forEach((step, index) => {
      if (index + 1 < this.currentStep) {
        step.classList.add("completed");
      } else if (index + 1 === this.currentStep) {
        step.classList.add("active");
      } else {
        step.classList.remove("active", "completed");
      }
    });

    // 質問パネルの表示切り替え
    document.querySelectorAll(".question-panel").forEach((panel, index) => {
      panel.style.display = index + 1 === this.currentStep ? "block" : "none";
    });

    // ボタンの有効/無効状態の更新
    document.getElementById("prevButton").disabled = this.currentStep === 1;
    document.getElementById("nextButton").textContent =
      this.currentStep === this.totalSteps ? "完了" : "次へ";
  }

  /**
   * 回答を保存
   * @param {string} questionId 質問ID
   * @param {string} answer 回答
   */
  saveAnswer(questionId, answer) {
    this.answers[questionId] = answer;
  }

  /**
   * 診断結果の生成
   * @returns {Object} 推奨されるビジネスモデルと理由
   */
  generateResult() {
    // 回答に基づいてビジネスモデルを推論
    const result = this.analyzeAnswers();

    // 結果の表示
    const resultPanel = document.getElementById("resultPanel");
    resultPanel.innerHTML = `
            <h3>推奨ビジネスモデル: ${result.modelType}</h3>
            <p>${result.reason}</p>
            <div class="mt-4">
                <button onclick="createBusinessModel('${result.modelType}')"
                        class="btn btn-primary">
                    このモデルで作成
                </button>
            </div>
        `;
  }
}

// ウィザードの初期化
document.addEventListener("DOMContentLoaded", () => {
  const wizard = new WizardState();
  wizard.updateUI();
});
