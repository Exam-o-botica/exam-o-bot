function main(form_url) {

  // form_url = "docs.google.com/forms/d/1WlvO6r5-7CvkjCvL7y80yhV4UqtFqpgIln-xQmVatas/edit"
  var form = FormApp.openByUrl(form_url);
  var items = form.getItems();

  var result = {
    "metadata": getFormMetadata(form),
    "items": items.map(itemToObject),
    "count": items.length
  };

  sendEmail("fiodor.vanchugov@gmail.com", result)

  return result;
}

/** If we want to receive data by email
 * Sends JSON as text to recipient email
 * @param recipient: String
 * @param result: JSON
 */
function sendEmail(recipient, json_file){
  var subject = "google form json import"
  var body = JSON.stringify(json_file);
  Logger.log(body);
  MailApp.sendEmail(recipient, subject, body);
}

/**
 * Returns the form metadata object for the given Form object.
 * @param form: Form
 * @returns (Object) object of form metadata.
 */
function getFormMetadata(form) {
  return {
    "title": form.getTitle(),
    "id": form.getId(),
    "description": form.getDescription(),
    "publishedUrl": form.getPublishedUrl(),
    "editorEmails": form.getEditors().map(function(user) { return user.getEmail() }),
    "count": form.getItems().length,
    "confirmationMessage": form.getConfirmationMessage(),
    "customClosedFormMessage": form.getCustomClosedFormMessage()
  };
}

/**
 * Returns an Object for a given Item.
 * @param item: Item
 * @returns (Object) object for the given item.
 */
function itemToObject(item) {
  var data = {};

  data.type = item.getType().toString();

  // Downcast items to access type-specific properties

  var itemTypeConstructorName = snakeCaseToCamelCase("AS_" + item.getType().toString() + "_ITEM");
  var typedItem = item[itemTypeConstructorName]();

  // Keys with a prefix of "get" have "get" stripped

  var getKeysRaw = Object.keys(typedItem).filter(function(s) {return s.indexOf("get") == 0});

  getKeysRaw.map(function(getKey) {
    var propName = getKey[3].toLowerCase() + getKey.substr(4);

    // Image data, choices, and type come in the form of objects / enums
    if (["image", "choices", "type", "alignment"].indexOf(propName) != -1) {return};

    // Skip feedback-related keys
    if ("getFeedbackForIncorrect".match(getKey) || "getFeedbackForCorrect".match(getKey)
      || "getGeneralFeedback".match(getKey)) {return};

    var propValue = typedItem[getKey]();

    data[propName] = propValue;
  });

  // Bool keys are included as-is

  var boolKeys = Object.keys(typedItem).filter(function(s) {
    return (s.indexOf("is") == 0) || (s.indexOf("has") == 0) || (s.indexOf("includes") == 0);
  });

  boolKeys.map(function(boolKey) {
    var propName = boolKey;
    var propValue = typedItem[boolKey]();
    data[propName] = propValue;
  });

  // Handle image data and list choices

  switch (item.getType()) {
    case FormApp.ItemType.LIST:
    case FormApp.ItemType.CHECKBOX:
      data.choices = typedItem.getChoices().map(function(choice) {
        return choice.getValue()
      });
    case FormApp.ItemType.MULTIPLE_CHOICE:
      data.choices = typedItem.getChoices().map(function(choice) {
        gotoPage = choice.getGotoPage()
        if (gotoPage == null)
            return choice.getValue()
        else
            return {
                "value": choice.getValue(),
                "gotoPage":choice.getGotoPage().getId()
        };
      });
      break;

    case FormApp.ItemType.IMAGE:
      data.alignment = typedItem.getAlignment().toString();

      if (item.getType() == FormApp.ItemType.VIDEO) {
        return;
      }

      var imageBlob = typedItem.getImage();

      data.imageBlob = {
        "dataAsString": "", //imageBlob.getDataAsString(), - BLOB too big
        "name": imageBlob.getName(),
        "isGoogleType": imageBlob.isGoogleType()
      };

      break;

    case FormApp.ItemType.PAGE_BREAK:
      data.pageNavigationType = typedItem.getPageNavigationType().toString();
      break;

    default:
      break;
  }

  // Have to do this because for some reason Google Scripts API doesn't have a
  // native VIDEO type
  if (item.getType().toString() === "VIDEO") {
    data.alignment = typedItem.getAlignment().toString();
  }

  return data;
}

/**
 * Converts a SNAKE_CASE string to a camelCase string.
 * @param s: string in snake_case
 * @returns (string) the camelCase version of that string
 */
function snakeCaseToCamelCase(s) {
  return s.toLowerCase().replace(/(\_\w)/g, function(m) {return m[1].toUpperCase();});
}