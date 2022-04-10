{
	set -e
	source "/sw/csi/anaconda3/4.4.0/binary/anaconda3/etc/profile.d/conda.sh"
	module purge
	conda deactivate
	conda activate pytorch1.8
	: <<- EOF
	python train_classification.py --model pointnet2_cls_msg --log_dir pointnet2_cls_msg --num_category 40 --use_normals
	EOF

	python train_partseg.py --model pointnet2_part_seg_ssg --normal --log_dir pointnet2_part_seg_ssg
	exit 0;
}