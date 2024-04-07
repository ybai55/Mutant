import mutant
from mutant.config import Settings

mutant_api = mutant.get_api()

mutant_api.add_training(
    embedding=[[1.1, 2.3, 3.2], [4.5, 6.9, 4.4]],
    input_uri=["/images/3.png", "/images/5.png"],
    inference_class=["bicycle", "car"],
    label_class=["bicycle", "car"],
    model_space="sample_space"
)
mutant_api.add_unlabeled(
    embedding=[[1.1, 2.3, 3.2], [4.5, 6.9, 4.4]],
    input_uri=["/images/3.png", "/images/5.png"],
    inference_class=["bicycle", "car"],
    model_space="sample_space"
)
# mutant_api.process(training_dataset_name="training", unlabeled_dataset_name="production", model_space="sample_space")
# results = mutant_api.get_results(dataset_name="production", n_results=2)
print(mutant_api.count(model_space="sample_space"))

# throws
# return sqrt(add.reduce(s, axis=axis, keepdims=keepdims))
# numpy.AxisError: axis 1 is out of bounds for array of dimension 1
