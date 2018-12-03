package job.fscience.com.xposition;

import android.app.Dialog;
import android.content.Context;
import android.os.Bundle;
import android.view.View;
import job.fscience.com.lib.DoubleSlideSeekBar;

public class AnimationSettingDialog extends Dialog {
    AnimationSettingClick callback = null;
    DoubleSlideSeekBar seekBar = null;

    float minValue = 0;
    float maxValue = 100;

    public AnimationSettingDialog(Context context) {
        super(context);
    }

    public AnimationSettingDialog(Context context, int themeResId) {
        super(context, themeResId);
    }

    public AnimationSettingDialog(Context context, boolean cancelable, OnCancelListener cancelListener) {
        super(context, cancelable, cancelListener);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        setContentView(R.layout.dialog_animation_setting);

        findViewById(R.id.confirm_action).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (callback != null) {
                    callback.onConfirmClick();
                }
                AnimationSettingDialog.this.dismiss();
            }
        });

        findViewById(R.id.cancel_action).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                AnimationSettingDialog.this.dismiss();
            }
        });


        seekBar = findViewById(R.id.seekbar);
        seekBar.setOnRangeListener(new DoubleSlideSeekBar.onRangeListener() {
            @Override
            public void onRange(float low, float big) {
                minValue = low;
                maxValue = big;
            }
        });
    }

    public void setCallback(AnimationSettingClick callback) {
        this.callback = callback;
    }

    public float getMinValue() {
        return minValue;
    }

    public float getMaxValue() {
        return maxValue;
    }

    public interface AnimationSettingClick {
        void onConfirmClick();
    }
}
