<?php
    require_once("utils.php");

    $num_lines = [];
    $files = scandir ( "../cache" );
    foreach ($files as $file) {
        if (endsWith( $file, ".moderate") ) {
            $lines = file( "../cache/" . $file, FILE_IGNORE_NEW_LINES);
            $num_lines[$file] = count($lines);
        }
    }
?>

<html>

    <head>
        <title>Neatza App Admin Panel</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
        <link type="text/css" rel="stylesheet" href="index.css" media="all" />
    </head>

    <body>
<?php foreach ($num_lines as $key => $value) { ?>
        <a href="/moderation.php?group=<?php echo $key ?>"><?php echo "$key ($value elements)" ?></a><br/>
<?php } ?>

    </body>

</html>
